#!/usr/bin/env python3
"""
Test script to verify multi-SDK setup.
"""
from pathlib import Path
import json


def check_sdk_setup():
    """Check the multi-SDK setup."""
    base_dir = Path(__file__).parent.parent
    samples_dir = base_dir / "samples"

    print("🔍 Checking Multi-SDK Setup")
    print("=" * 60)

    # Check samples directory
    if not samples_dir.exists():
        print(f"❌ Samples directory not found: {samples_dir}")
        return

    print(f"📁 Samples directory: {samples_dir}")
    print()

    # Check for SDKs
    sdks_found = []
    for sdk_dir in sorted(samples_dir.iterdir()):
        if sdk_dir.is_dir() and not sdk_dir.name.startswith('.'):
            # Count samples
            if sdk_dir.name == "clerk":
                samples = list(sdk_dir.glob("task*"))
            elif sdk_dir.name == "lancedb":
                samples = list(sdk_dir.glob("lancedb_task*"))
            else:
                samples = list(sdk_dir.glob("*task*"))

            if samples:
                sdks_found.append({
                    "name": sdk_dir.name,
                    "path": sdk_dir,
                    "sample_count": len(samples),
                    "sample_pattern": samples[0].name if samples else "N/A"
                })

    # Report findings
    if sdks_found:
        print("✅ Found SDKs:")
        for sdk_info in sdks_found:
            print(f"\n  📦 {sdk_info['name'].upper()}")
            print(f"     Path: {sdk_info['path']}")
            print(f"     Samples: {sdk_info['sample_count']}")
            print(f"     Pattern: {sdk_info['sample_pattern']}")

            # Check for manifest
            manifest_path = sdk_info['path'] / f"{sdk_info['name']}_dataset_manifest.json"
            if manifest_path.exists():
                with open(manifest_path) as f:
                    manifest = json.load(f)
                print(f"     Manifest: ✓ (v{manifest.get('dataset_version', 'unknown')})")
                if "by_task_type" in manifest:
                    task_types = manifest["by_task_type"]
                    print(f"     Task distribution: {task_types}")
            else:
                print(f"     Manifest: ✗")

            # Check sample structure
            first_sample = list(sdk_info['path'].iterdir())[0]
            if first_sample.is_dir():
                subdirs = [d.name for d in first_sample.iterdir() if d.is_dir()]
                print(f"     Sample structure: {', '.join(subdirs)}")
    else:
        print("❌ No SDKs found with samples")

    print()
    print("=" * 60)

    # Check if Clerk samples are in the right place
    clerk_old = samples_dir.parent / "samples" / "task1_initialization_001"
    if clerk_old.exists():
        print("⚠️  Found Clerk samples in old location (samples root)")
        print("   Consider moving them to samples/clerk/")

    # Summary
    print("\n📊 Summary:")
    print(f"   Total SDKs: {len(sdks_found)}")
    total_samples = sum(sdk["sample_count"] for sdk in sdks_found)
    print(f"   Total samples: {total_samples}")

    if len(sdks_found) >= 2:
        print("\n✅ Multi-SDK setup is ready!")
    else:
        print("\n⚠️  Only one SDK found. Add more SDKs for multi-SDK evaluation.")


if __name__ == "__main__":
    check_sdk_setup()