import subprocess
import sys
import argparse
import re

class SemVer:
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self):
        return f"v{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other):
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __eq__(self, other):
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __gt__(self, other):
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

def make_semver(version_str: str) -> SemVer:
    # Find the first three integers
    # Example cases: 0.0.0, 02.01.0-alpha, v1.1.1
    matches = re.findall(r'\d+', version_str)
    if len(matches) < 3:
        raise ValueError(f"Invalid version format: {version_str}")
    major, minor, patch = map(int, matches[:3])
    return SemVer(major, minor, patch)


def run_command(command, exit_on_error=True):
    """Executes a git command and returns the output."""
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if exit_on_error:
            print(f"Error: {e.stderr}")
            sys.exit(1)
        raise e


def highest_semver(versions: list[SemVer]) -> SemVer:
    highest = SemVer(0, 0, 0)
    for sv in versions:
        try:
            if sv > highest:
                highest = sv
        except ValueError:
            continue        
    return highest


def get_tags() -> list[SemVer]:
    svs: list[SemVer] = []
    tags = run_command(['git', 'tag'], exit_on_error=False).splitlines()
    for tag in tags:
        try:
            sv = make_semver(tag)
            svs.append(sv)
        except ValueError:
            continue
    return  svs


def bump_tag(part):
    tags = get_tags()
    sv = highest_semver(tags)
    print(f"Highest SemVer: {sv}")

    # Increment the version based on input
    if part == 'major':
        sv.major += 1
        sv.minor = 0
        sv.patch = 0
    elif part == 'minor':
        sv.minor += 1
        sv.patch = 0
    elif part == 'patch':
        sv.patch += 1
    
    print(f"Bumping to: {sv}")

    # Create the new tag locally
    run_command(['git', 'tag', '-a', str(sv), '-m', f"Bumping version to {sv}"])
    
    # Push the new tag to origin
    run_command(['git', 'push', 'origin', sv])
    print(f"Successfully pushed {sv} to origin.")

def run():
    parser = argparse.ArgumentParser(description="Bump Git tag for releases (SemVer)")
    parser.add_argument(
        'part', 
        choices=['major', 'minor', 'patch'], 
        nargs='?',
        help="The part of the version to bump"
    )
    
    args = parser.parse_args()
    
    if args.part is None:
        tags = get_tags()
        sv = highest_semver(tags)
        print(f"Latest tag: {sv}")
        print("\nTo bump the version, specify which part:")
        parser.print_help()
    else:
        bump_tag(args.part)
