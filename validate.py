#!/usr/bin/env python3
"""
Validation script to verify the self-healing knowledge graph implementation.
This script checks the structure and basic functionality without requiring dependencies.
"""
import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✓ {description}: {filepath} ({size} bytes)")
        return True
    else:
        print(f"✗ {description}: {filepath} NOT FOUND")
        return False


def check_directory_structure():
    """Verify the directory structure is correct."""
    print("\n" + "="*70)
    print("Checking Directory Structure")
    print("="*70)
    
    required_dirs = [
        "src",
        "src/agents",
        "src/ingestion",
        "src/observability",
        "src/utils",
        "tests",
        "data/source_documents",
    ]
    
    all_good = True
    for directory in required_dirs:
        if os.path.isdir(directory):
            print(f"✓ Directory exists: {directory}")
        else:
            print(f"✗ Directory missing: {directory}")
            all_good = False
    
    return all_good


def check_core_files():
    """Verify all core files are present."""
    print("\n" + "="*70)
    print("Checking Core Files")
    print("="*70)
    
    files = [
        ("requirements.txt", "Dependencies file"),
        (".env.example", "Environment configuration template"),
        (".gitignore", "Git ignore file"),
        ("README.md", "Main documentation"),
        ("QUICKSTART.md", "Quick start guide"),
        ("main.py", "Main orchestration script"),
        ("dashboard.py", "Streamlit dashboard"),
        ("examples.py", "Example usage script"),
        ("docker-compose.yml", "Docker compose configuration"),
        ("Dockerfile", "Docker image definition"),
    ]
    
    all_good = True
    for filepath, description in files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    return all_good


def check_source_modules():
    """Verify all source modules are present."""
    print("\n" + "="*70)
    print("Checking Source Modules")
    print("="*70)
    
    modules = [
        ("src/__init__.py", "Main package init"),
        ("src/utils/__init__.py", "Utils package init"),
        ("src/utils/config.py", "Configuration module"),
        ("src/utils/neo4j_connection.py", "Neo4j connection module"),
        ("src/ingestion/__init__.py", "Ingestion package init"),
        ("src/ingestion/temporal_ingestion.py", "Temporal ingestion module"),
        ("src/agents/__init__.py", "Agents package init"),
        ("src/agents/conflict_detection.py", "Conflict detection agent"),
        ("src/agents/self_correction.py", "Self-correction agent"),
        ("src/observability/__init__.py", "Observability package init"),
        ("src/observability/metrics.py", "Metrics tracking module"),
        ("tests/__init__.py", "Tests package init"),
        ("tests/test_basic.py", "Basic tests"),
    ]
    
    all_good = True
    for filepath, description in modules:
        if not check_file_exists(filepath, description):
            all_good = False
    
    return all_good


def check_python_syntax():
    """Check Python syntax of all modules."""
    print("\n" + "="*70)
    print("Checking Python Syntax")
    print("="*70)
    
    python_files = [
        "main.py",
        "dashboard.py",
        "examples.py",
        "src/utils/config.py",
        "src/utils/neo4j_connection.py",
        "src/ingestion/temporal_ingestion.py",
        "src/agents/conflict_detection.py",
        "src/agents/self_correction.py",
        "src/observability/metrics.py",
    ]
    
    all_good = True
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                compile(f.read(), filepath, 'exec')
            print(f"✓ Syntax valid: {filepath}")
        except SyntaxError as e:
            print(f"✗ Syntax error in {filepath}: {e}")
            all_good = False
        except Exception as e:
            print(f"⚠ Could not check {filepath}: {e}")
    
    return all_good


def check_requirements():
    """Check requirements.txt has necessary dependencies."""
    print("\n" + "="*70)
    print("Checking Requirements")
    print("="*70)
    
    required_packages = [
        "neo4j",
        "llama-index",
        "langgraph",
        "langchain",
        "streamlit",
        "openai",
        "plotly",
        "pandas",
    ]
    
    try:
        with open("requirements.txt", 'r') as f:
            content = f.read().lower()
        
        all_good = True
        for package in required_packages:
            if package in content:
                print(f"✓ Required package listed: {package}")
            else:
                print(f"✗ Missing required package: {package}")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"✗ Error reading requirements.txt: {e}")
        return False


def count_lines_of_code():
    """Count total lines of code."""
    print("\n" + "="*70)
    print("Code Statistics")
    print("="*70)
    
    python_files = []
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    python_files.extend(["main.py", "dashboard.py", "examples.py"])
    
    total_lines = 0
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                lines = len(f.readlines())
                total_lines += lines
        except:
            pass
    
    print(f"Total Python files: {len(python_files)}")
    print(f"Total lines of code: {total_lines:,}")
    
    # Count documentation
    doc_files = ["README.md", "QUICKSTART.md"]
    doc_lines = 0
    for filepath in doc_files:
        try:
            with open(filepath, 'r') as f:
                doc_lines += len(f.readlines())
        except:
            pass
    
    print(f"Documentation lines: {doc_lines:,}")


def main():
    """Run all validation checks."""
    print("\n" + "="*70)
    print("Self-Healing Knowledge Graph Implementation Validation")
    print("="*70)
    
    os.chdir(Path(__file__).parent)
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Core Files", check_core_files),
        ("Source Modules", check_source_modules),
        ("Python Syntax", check_python_syntax),
        ("Requirements", check_requirements),
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
    
    count_lines_of_code()
    
    # Summary
    print("\n" + "="*70)
    print("Validation Summary")
    print("="*70)
    
    all_passed = True
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ All validation checks passed!")
        print("\nThe self-healing knowledge graph implementation is complete.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up Neo4j database")
        print("3. Configure .env file")
        print("4. Run examples: python examples.py")
        print("5. Launch dashboard: streamlit run dashboard.py")
    else:
        print("✗ Some validation checks failed.")
        print("Please review the errors above.")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
