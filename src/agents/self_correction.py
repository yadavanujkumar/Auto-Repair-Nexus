"""
Self-Correction Agent with Deep Research capabilities.
Resolves conflicts by analyzing source documents and updating the graph.
"""
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import OpenAI

from ..utils.neo4j_connection import Neo4jConnection
from ..utils.config import load_config
from .conflict_detection import SemanticConflict


class DeepResearchTask:
    """Handles deep research into source documents to resolve conflicts."""
    
    def __init__(self, openai_client: OpenAI):
        """Initialize the deep research task handler."""
        self.client = openai_client
        
    def analyze_source_documents(
        self,
        conflict: SemanticConflict,
        source_docs: List[str],
    ) -> Dict[str, Any]:
        """
        Analyze source documents to determine the most accurate fact.
        Returns a decision with reasoning.
        """
        # Prepare context for LLM
        context = self._prepare_conflict_context(conflict)
        docs_text = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(source_docs)])
        
        prompt = f"""You are a fact-checking agent analyzing conflicting information in a knowledge graph.

Conflict Details:
{context}

Source Documents:
{docs_text}

Task: Analyze the source documents and determine:
1. Which relationship is most accurate and current?
2. What is the confidence level (0.0 to 1.0)?
3. Should any relationships be marked as outdated?
4. Provide reasoning for your decision.

Respond in JSON format:
{{
    "correct_relationship_id": "...",
    "confidence": 0.95,
    "outdated_relationship_ids": ["..."],
    "reasoning": "...",
    "supporting_evidence": "..."
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert fact-checker and knowledge graph curator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            decision = json.loads(response.choices[0].message.content)
            decision["tokens_used"] = response.usage.total_tokens
            
            return decision
            
        except Exception as e:
            print(f"Error in deep research: {e}")
            return {
                "error": str(e),
                "confidence": 0.0,
                "reasoning": "Failed to analyze source documents"
            }
            
    def _prepare_conflict_context(self, conflict: SemanticConflict) -> str:
        """Prepare conflict information as text for LLM."""
        context = f"""
Entity: {conflict.entity_name} (ID: {conflict.entity_id})
Relationship Type: {conflict.relationship_type}
Severity: {conflict.severity}

Conflicting Relationships:
"""
        for i, rel in enumerate(conflict.conflicting_relationships, 1):
            context += f"\n{i}. ID: {rel.get('id')}"
            context += f"\n   Target: {rel.get('target')}"
            context += f"\n   Timestamp: {rel.get('timestamp')}"
            context += f"\n   Confidence: {rel.get('confidence', 'N/A')}"
            context += f"\n   Source: {rel.get('source_document', 'Unknown')}"
            if rel.get('properties'):
                context += f"\n   Properties: {json.dumps(rel['properties'])}"
            context += "\n"
            
        return context


class SelfCorrectionAgent:
    """
    Agent that performs self-correction on the knowledge graph.
    Uses deep research to resolve conflicts and update the graph.
    """
    
    def __init__(self, neo4j_conn: Neo4jConnection, openai_api_key: Optional[str] = None):
        """Initialize the self-correction agent."""
        self.conn = neo4j_conn
        config = load_config()
        api_key = openai_api_key or config.openai.api_key
        self.openai_client = OpenAI(api_key=api_key)
        self.research_task = DeepResearchTask(self.openai_client)
        self.total_tokens_used = 0
        self.corrections_made = 0
        
    def fetch_source_documents(self, conflict: SemanticConflict) -> List[str]:
        """
        Fetch source documents related to the conflict.
        In a real system, this would retrieve actual documents from storage.
        """
        source_docs = []
        
        for rel in conflict.conflicting_relationships:
            source_doc = rel.get("source_document")
            if source_doc:
                # In production, fetch actual document content
                # For now, create a summary
                doc_text = f"""
Source Document: {source_doc}
Entity: {conflict.entity_name}
Relationship: {conflict.relationship_type} -> {rel.get('target')}
Timestamp: {rel.get('timestamp')}
Confidence: {rel.get('confidence', 1.0)}
Additional Info: {json.dumps(rel.get('properties', {}))}
"""
                source_docs.append(doc_text)
            else:
                # Create placeholder if no source
                source_docs.append(f"Relationship to {rel.get('target')} (no source document)")
                
        return source_docs
        
    def apply_correction(
        self,
        conflict: SemanticConflict,
        decision: Dict[str, Any],
    ) -> bool:
        """
        Apply the correction to the knowledge graph using Cypher.
        Updates relationships based on the research decision.
        """
        try:
            correct_rel_id = decision.get("correct_relationship_id")
            outdated_rel_ids = decision.get("outdated_relationship_ids", [])
            confidence = decision.get("confidence", 1.0)
            reasoning = decision.get("reasoning", "")
            
            # Mark correct relationship as current with updated confidence
            if correct_rel_id:
                update_correct = """
                MATCH ()-[r:RELATED_TO {id: $rel_id}]->()
                SET r.is_current = true,
                    r.confidence = $confidence,
                    r.verified_at = $timestamp,
                    r.verification_reasoning = $reasoning
                RETURN r.id
                """
                
                self.conn.execute_write(update_correct, {
                    "rel_id": correct_rel_id,
                    "confidence": confidence,
                    "timestamp": datetime.utcnow().isoformat(),
                    "reasoning": reasoning,
                })
                
            # Mark outdated relationships
            if outdated_rel_ids:
                update_outdated = """
                MATCH ()-[r:RELATED_TO]->()
                WHERE r.id IN $rel_ids
                SET r.is_current = false,
                    r.outdated_at = $timestamp,
                    r.outdated_reasoning = $reasoning
                RETURN count(r) as updated_count
                """
                
                self.conn.execute_write(update_outdated, {
                    "rel_ids": outdated_rel_ids,
                    "timestamp": datetime.utcnow().isoformat(),
                    "reasoning": reasoning,
                })
                
            # Update entity to clear conflict flag
            clear_conflict = """
            MATCH (e:Entity {id: $entity_id})
            SET e.has_conflict = false,
                e.last_healed_at = $timestamp,
                e.healing_count = COALESCE(e.healing_count, 0) + 1
            RETURN e.id
            """
            
            self.conn.execute_write(clear_conflict, {
                "entity_id": conflict.entity_id,
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            # Mark conflict as resolved
            resolve_conflict = """
            MATCH (c:ConflictLog {id: $conflict_id})
            SET c.resolved = true,
                c.resolved_at = $timestamp,
                c.resolution_decision = $decision
            RETURN c.id
            """
            
            self.conn.execute_write(resolve_conflict, {
                "conflict_id": conflict.conflict_id,
                "timestamp": datetime.utcnow().isoformat(),
                "decision": json.dumps(decision),
            })
            
            self.corrections_made += 1
            return True
            
        except Exception as e:
            print(f"Error applying correction: {e}")
            return False
            
    def heal_conflict(self, conflict: SemanticConflict) -> Dict[str, Any]:
        """
        Complete healing process for a single conflict:
        1. Fetch source documents
        2. Perform deep research
        3. Apply correction
        """
        print(f"\n[HEALING] {conflict.description}")
        
        # Fetch source documents
        source_docs = self.fetch_source_documents(conflict)
        
        # Perform deep research
        decision = self.research_task.analyze_source_documents(conflict, source_docs)
        
        # Track token usage
        tokens_used = decision.get("tokens_used", 0)
        self.total_tokens_used += tokens_used
        
        # Apply correction if decision is confident
        if decision.get("confidence", 0) >= 0.7 and not decision.get("error"):
            success = self.apply_correction(conflict, decision)
            
            return {
                "conflict_id": conflict.conflict_id,
                "success": success,
                "decision": decision,
                "tokens_used": tokens_used,
            }
        else:
            print(f"⚠ Low confidence or error, skipping correction")
            return {
                "conflict_id": conflict.conflict_id,
                "success": False,
                "decision": decision,
                "tokens_used": tokens_used,
                "reason": "Low confidence or error in research",
            }
            
    def heal_all_conflicts(self, conflicts: List[SemanticConflict]) -> Dict[str, Any]:
        """
        Heal all provided conflicts and return summary statistics.
        """
        results = []
        
        print(f"\n{'='*60}")
        print(f"Starting self-healing process for {len(conflicts)} conflicts")
        print(f"{'='*60}")
        
        for conflict in conflicts:
            result = self.heal_conflict(conflict)
            results.append(result)
            
        successful = sum(1 for r in results if r.get("success"))
        
        summary = {
            "total_conflicts": len(conflicts),
            "successful_corrections": successful,
            "failed_corrections": len(conflicts) - successful,
            "total_tokens_used": self.total_tokens_used,
            "results": results,
        }
        
        print(f"\n{'='*60}")
        print(f"Self-healing complete:")
        print(f"  ✓ Successful: {successful}/{len(conflicts)}")
        print(f"  ✗ Failed: {len(conflicts) - successful}/{len(conflicts)}")
        print(f"  💰 Tokens used: {self.total_tokens_used:,}")
        print(f"{'='*60}\n")
        
        return summary
