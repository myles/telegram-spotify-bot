import os.path

from fabric import api
from fabric.operations import put
from fabric.utils import puts, abort
from fabric.contrib.files import exists

api.env.hosts = ['bear']
api.env.use_ssh_config = True
api.env.remote_interrupt = True

api.env.supervisord_name = 'telegram-myles-bot'

# Directories
api.env.root_dir = '/home/myles/Projects/telegram-spotify-bot'
api.env.proj_dir = os.path.join(api.env.root_dir)
api.env.venv_dir = os.path.join(api.env.root_dir, 'venv')

# Python Bullshit
api.env.venv_python = os.path.join(api.env.venv_dir, 'bin/python')
api.env.venv_pip = os.path.join(api.env.venv_dir, 'bin/pip')

# Git Bullshit
api.env.repo = 'git://github.com/myles/telegram-spotify-bot.git'
api.env.remote = 'origin'
api.env.branch = 'master'

# Files
api.env.bot_log = os.path.join(api.env.proj_dir, 'bot.log')
api.env.config_json = os.path.join(api.env.proj_dir, 'config.json')


@api.task
def setup():
    """
    Setup the deploy server.
    """
    # Make a bunch of the directories.
    api.sudo('mkdir -p {0}'.format(' '.join([api.env.proj_dir,
                                             api.env.venv_dir])))

    if not exists(os.path.join(api.env.proj_dir, '.git')):
        # Clone the GitHub Repo
        with api.cd(api.env.proj_dir):
            api.run('git clone {0} .'.format(api.env.repo))

    # Make sure the directories are writeable by me.
    api.sudo('chown myles:myles {0}'.format(' '.join([api.env.proj_dir,
                                                      api.env.venv_dir])))

    # Createh virtual environment.
    if not exists(api.env.venv_dir):
        api.run('virtualenv {0}'.format(api.env.venv_dir))

    # Install the dependencies.
    pip_upgrade()


@api.task
def python_version():
    """
    Return the Python version on the server for testing.
    """
    with api.cd(api.env.proj_dir):
        api.run("{0} -V".format(api.env.venv_python))


@api.task
def update_code():
    """
    Update to the latest version of the code.
    """
    with api.cd(api.env.proj_dir):
        api.run('git reset --hard HEAD')
        api.run('git checkout {0}'.format(api.env.branch))
        api.run('git pull {0} {1}'.format(api.env.remote, api.env.branch))


@api.task
def pip_upgrade():
    """
    Upgrade the third party Python libraries.
    """
    with api.cd(api.env.proj_dir):
        api.run('{0} install --upgrade -r '
                'requirements.txt'.format(api.env.venv_pip))


@api.task
def supervisorctl_restart():
    """
    Restart the supervisord process.
    """
    api.sudo('supervisorctl restart {0}'.format(api.env.supervisord_name))


@api.task
@api.parallel
def tail():
    assert(api.env.remote_interrupt is True)
    with api.settings(warn_only=True):
        api.run('tail -n 50 -f {0}'.format(api.env.bot_log))


@api.task
def copy_config():
    put(local_path='config.json', remote_path=api.env.config_json)


@api.task
def ship_it():
    # Check to make sure that there isn't any unchecked files
    git_status = api.local('git status --porcelain', capture=True)

    if git_status:
        abort('There are unchecked files.')

    # Push the repo to the remote
    api.local('git push {0} {1}'.format(api.env.remote, api.env.branch))

    # The deploy tasks
    update_code()
    pip_upgrade()
    copy_config()
    supervisorctl_restart()

    # Draw a ship
    puts("                           |    |    |                           ")
    puts("                          )_)  )_)  )_)                          ")
    puts("                         )___))___))___)\                        ")
    puts("                        )____)____)_____)\\                      ")
    puts("                      _____|____|____|____\\\__                  ")
    puts("             ---------\                   /---------             ")
    puts("               ^^^^^ ^^^^^^^^^^^^^^^^^^^^^                       ")
    puts("                 ^^^^      ^^^^     ^^^    ^^                    ")
    puts("                      ^^^^      ^^^                              ")
