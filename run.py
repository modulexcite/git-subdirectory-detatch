import argparse
import os
import shutil
import subprocess
import sys

# convert windows paths to unix paths for folder depths > 1
def unixify_path(path):
    if sys.platform == 'win32' and subdirectory_path.count('\\') > 1:
        return subdirectory_path.replace('\\', '/')
    return path

new_remote = None

if len(sys.argv) > 1:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--repo_dir',
        type=str,
        nargs='?',
        help='Path of original repo.')
    parser.add_argument(
        '--output_dir',
        type=str,
        nargs='?',
        help='Path of final output directory.')
    parser.add_argument(
        '--subdirectory_path',
        type=str,
        nargs='?',
        help='Subdirectory path to isolate (relative to repo directory):')
    parser.add_argument(
        '-new_remote',
        type=str,
        nargs='?',
        help='New remote repo.')
    args = parser.parse_args()

    original_repo_path = args.repo_dir
    new_repo_path = args.output_dir
    subdirectory_path = args.subdirectory_path
    new_remote = args.new_remote
else:
    original_repo_path = raw_input('Path of original repo: ')
    new_repo_path = raw_input('Path of final output directory: ')
    subdirectory_path = raw_input(
        'Subdirectory path to isolate (relative to %s): ' %
        new_repo_path)
    new_remote = raw_input('New remote repo (optional): ')
if not os.path.exists(new_repo_path):
    os.makedirs(new_repo_path)
else:
    print 'OUTPUT DIRECTORY ALREADY EXISTS'
    sys.exit(0)

# clone original repo to new working repo
print 'Cloning original repo...'
subprocess.call(['git',
                 'clone',
                 '--no-hardlinks',
                 original_repo_path,
                 new_repo_path])

os.chdir(new_repo_path)

unix_subdirectory_path = unixify_path(subdirectory_path)

# discard everything but our subdirectory, promote to root level
print 'Discarding unwanted changes...'
subprocess.call(['git',
                 'filter-branch',
                 '--subdirectory-filter',
                 unix_subdirectory_path,
                 'HEAD',
                 '--',
                 '--all'])
subprocess.call(['git', 'reset', '--hard'])

# cleanup
print 'Cleaning up...'
subprocess.call(['git', 'gc', '--aggressive'])
subprocess.call(['git', 'prune'])

# origin stuff
print 'Removing old origin..'
subprocess.call(['git', 'remote', 'rm', 'origin'])
if new_remote:
    subprocess.call(['git', 'remote', 'add', 'origin', new_remote])

# remove from original repo
print "Removing subdirectory from original repository"
os.chdir(original_repo_path)
shutil.rmtree(os.path.abspath(subdirectory_path))
subprocess.call(['git',
                 'add',
                 '-u',
                 unix_subdirectory_path])
subprocess.call(['git',
                 'commit',
                 '-m',
                 'Detatched %s into separate repository' % subdirectory_path])
