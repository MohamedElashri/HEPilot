#!/usr/bin/env python3
"""
HEPilot ArXiv Adapter Compliance Test
Tests the adapter implementation against the HEPilot specification requirements.
"""

import json
import hashlib
import uuid
import jsonschema
from pathlib import Path
from typing import Dict, Any, List
import sys
import os

# Add the adapter directory to the path
sys.path.append('adapters/hep_adapter_arxiv_lhcb')

class ComplianceChecker:
    """Checks adapter compliance against HEPilot specifications."""
    
    def __init__(self, adapter_dir: Path, standards_dir: Path):
        """Initialize the compliance checker.
        
        Args:
            adapter_dir: Path to the adapter implementation
            standards_dir: Path to the HEPilot standards directory
        """
        self.adapter_dir = adapter_dir
        self.standards_dir = standards_dir
        self.schemas_dir = standards_dir / "schemas"
        self.issues: List[str] = []
        self.passed_tests: List[str] = []
        
    def load_schema(self, schema_name: str) -> Dict[str, Any]:
        """Load a JSON schema from the standards directory."""
        schema_path = self.schemas_dir / f"{schema_name}.schema.json"
        with open(schema_path, 'r') as f:
            return json.load(f)
    
    def check_adapter_config_compliance(self) -> bool:
        """Check adapter configuration compliance."""
        print("🔍 Checking adapter configuration compliance...")
        
        config_path = self.adapter_dir / "adapter_config.json"
        if not config_path.exists():
            self.issues.append("❌ adapter_config.json not found")
            return False
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Load the adapter config schema
        schema = self.load_schema("adapter_config")
        
        try:
            # Validate against schema
            jsonschema.validate(config, schema)
            self.passed_tests.append("✅ Configuration structure is valid")
        except jsonschema.ValidationError as e:
            self.issues.append(f"❌ Configuration schema validation failed: {e.message}")
            return False
        
        # Check config hash
        adapter_config = config["adapter_config"]
        config_hash = adapter_config.get("config_hash", "")
        
        if not config_hash or len(config_hash) != 64:
            self.issues.append("❌ config_hash is missing or invalid (must be 64-character SHA-256 hex)")
        else:
            # Verify config hash
            config_copy = dict(adapter_config)
            config_copy.pop("config_hash", None)
            canonical_json = json.dumps(config_copy, sort_keys=True, separators=(',', ':'))
            expected_hash = hashlib.sha256(canonical_json.encode()).hexdigest()
            
            if config_hash.lower() != expected_hash.lower():
                self.issues.append(f"❌ config_hash mismatch. Expected: {expected_hash}, Got: {config_hash}")
            else:
                self.passed_tests.append("✅ Configuration hash is correct")
        
        # Check version format
        version = adapter_config.get("version", "")
        if not version or not self._is_valid_semver(version):
            self.issues.append("❌ Version must follow semantic versioning (e.g., 1.0.0)")
        else:
            self.passed_tests.append("✅ Version format is correct")
        
        # Check chunk_size range
        chunk_size = adapter_config.get("processing_config", {}).get("chunk_size", 0)
        if not (512 <= chunk_size <= 4096):
            self.issues.append("❌ chunk_size must be between 512 and 4096")
        else:
            self.passed_tests.append("✅ Chunk size is within valid range")
        
        # Check chunk_overlap range
        chunk_overlap = adapter_config.get("processing_config", {}).get("chunk_overlap", -1)
        if not (0.0 <= chunk_overlap < 1.0):
            self.issues.append("❌ chunk_overlap must be between 0.0 and 1.0 (exclusive)")
        else:
            self.passed_tests.append("✅ Chunk overlap is within valid range")
        
        return len(self.issues) == 0
    
    def check_required_files(self) -> bool:
        """Check that all required files are present."""
        print("🔍 Checking required files...")
        
        required_files = [
            "adapter_config.json",
            "hepilot_arxiv_adapter.py",
            "requirements.txt",
            "README.md"
        ]
        
        for file_name in required_files:
            file_path = self.adapter_dir / file_name
            if not file_path.exists():
                self.issues.append(f"❌ Required file missing: {file_name}")
            else:
                self.passed_tests.append(f"✅ Required file present: {file_name}")
        
        return all((self.adapter_dir / f).exists() for f in required_files)
    
    def check_arxiv_specific_requirements(self) -> bool:
        """Check arXiv-specific requirements from the specification."""
        print("🔍 Checking arXiv-specific requirements...")
        
        # Read the main adapter file
        adapter_file = self.adapter_dir / "hepilot_arxiv_adapter.py"
        with open(adapter_file, 'r') as f:
            adapter_code = f.read()
        
        # Check for required arXiv API usage
        if "export.arxiv.org/api/query" in adapter_code:
            self.passed_tests.append("✅ Uses arXiv REST API")
        else:
            self.issues.append("❌ Must use arXiv REST API (export.arxiv.org/api/query)")
        
        # Check for OAI-PMH usage
        if "export.arxiv.org/oai2" in adapter_code:
            self.passed_tests.append("✅ Uses arXiv OAI-PMH interface")
        else:
            self.issues.append("❌ Must use arXiv OAI-PMH interface (export.arxiv.org/oai2)")
        
        # Check for deduplication logic
        if "seen_ids" in adapter_code or "unique_docs" in adapter_code:
            self.passed_tests.append("✅ Implements deduplication logic")
        else:
            self.issues.append("❌ Must implement deduplication of results")
        
        return True
    
    def check_output_format_compliance(self) -> bool:
        """Check if output format follows the specification."""
        print("🔍 Checking output format specification...")
        
        # This would require running the adapter, so we'll check the code structure
        adapter_file = self.adapter_dir / "hepilot_arxiv_adapter.py"
        with open(adapter_file, 'r') as f:
            adapter_code = f.read()
        
        required_output_patterns = [
            ("chunks_dir", "chunks"),
            ("document_metadata.json", "document_metadata.json"),
            ("processing_metadata.json", "processing_metadata.json"), 
            ("full_document.md", "full_document.md"),
            ("catalog.json", "catalog.json")
        ]
        
        for pattern_name, pattern in required_output_patterns:
            if pattern in adapter_code:
                self.passed_tests.append(f"✅ Creates required output: {pattern}")
            else:
                self.issues.append(f"❌ Missing required output: {pattern}")
        
        return True
    
    def _is_valid_semver(self, version: str) -> bool:
        """Check if version follows semantic versioning."""
        import re
        pattern = r'^\d+\.\d+\.\d+$'
        return re.match(pattern, version) is not None
    
    def _is_valid_uuid(self, uuid_string: str) -> bool:
        """Check if string is a valid UUID."""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all compliance checks and return results."""
        print("🚀 Starting HEPilot ArXiv Adapter Compliance Check\n")
        
        # Run all checks
        self.check_required_files()
        self.check_adapter_config_compliance()
        self.check_arxiv_specific_requirements()
        self.check_output_format_compliance()
        
        # Generate report
        print("\n" + "="*60)
        print("📊 COMPLIANCE REPORT")
        print("="*60)
        
        print(f"\n✅ PASSED TESTS ({len(self.passed_tests)}):")
        for test in self.passed_tests:
            print(f"  {test}")
        
        if self.issues:
            print(f"\n❌ ISSUES FOUND ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  {issue}")
        else:
            print(f"\n🎉 NO ISSUES FOUND!")
        
        total_checks = len(self.passed_tests) + len(self.issues)
        compliance_score = (len(self.passed_tests) / total_checks * 100) if total_checks > 0 else 0
        
        print(f"\n📈 COMPLIANCE SCORE: {compliance_score:.1f}% ({len(self.passed_tests)}/{total_checks})")
        
        if compliance_score >= 90:
            print("🟢 EXCELLENT - Highly compliant with HEPilot specification")
        elif compliance_score >= 75:
            print("🟡 GOOD - Mostly compliant, minor issues to address")
        elif compliance_score >= 50:
            print("🟠 FAIR - Several compliance issues need attention")
        else:
            print("🔴 POOR - Major compliance issues require immediate attention")
        
        return {
            "passed_tests": self.passed_tests,
            "issues": self.issues,
            "compliance_score": compliance_score,
            "total_checks": total_checks
        }

def main():
    """Main function to run compliance checks."""
    # Setup paths
    base_dir = Path("/data/home/melashri/LLM/HEPilot")
    adapter_dir = base_dir / "adapters" / "hep_adapter_arxiv_lhcb"
    standards_dir = base_dir / "standards"
    
    # Create compliance checker
    checker = ComplianceChecker(adapter_dir, standards_dir)
    
    # Run checks
    results = checker.run_all_checks()
    
    # Return appropriate exit code
    return 0 if results["compliance_score"] >= 90 else 1

if __name__ == "__main__":
    exit(main())
