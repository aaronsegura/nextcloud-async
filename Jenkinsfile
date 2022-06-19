pipeline {
  agent any

  environment {
    NEXTCLOUD_VERSION="24"
    GROUPFOLDERS_VERSION="11.1.2"
    GROUPFOLDERS_ARCHIVE_NAME="groupfolders.tar.gz"
    GROUPFOLDERS_URL="https://github.com/nextcloud/groupfolders/releases/download/v${GROUPFOLDERS_VERSION}/${GROUPFOLDERS_ARCHIVE_NAME}"
    NEXTCLOUD_HOSTNAME="app"
    NEXTCLOUD_ADMIN_USER="admin"
    NEXTCLOUD_ADMIN_PASSWORD="admin"

    NEXTCLOUD_HOST="app"
    NEXTCLOUD_PORT="8181"
  }
  stages {

    stage('Install Package') {
      steps {
        withPythonEnv('python3') {
          sh 'python3 -mpip install .'
        }
      }
    }

    stage('Run Source Code Tests') {
      parallel {
        stage('flake8 check') {
          agent {
            docker {
              image 'pipelinecomponents/flake8'
              args '-v $PWD:/data'
            }
          }
          steps {
            sh 'flake8 --exclude .git,__pycache__,node_modules,.pyenv* --count --statistics . || true'
          }
        }
        stage('pydocstyle check') {
          agent {
            dockerfile {
              dir '.jenkins'
              filename 'Dockerfile-pydocstyle'
            }
          }
          steps {
            sh 'pydocstyle --convention=pep257 --count nextcloud_aio || true'
          }
        }
      }
    } // parallel
    stage('Build Nextcloud Node') {
      steps {
        dir('tests') {
          sh 'docker-compose build'
          sh 'docker-compose up -d'
        }
      }
    }
    stage('Unit testing') {
      steps {
        withPythonEnv('python3') {
          dir('tests') {
            sh 'python3 -munittest'
          }
        }
      }
    }
    stage('Tear down Nextcloud') {
      steps {
        dir('tests') {
          sh 'docker-compose stop'
          sh 'docker-compose rm'

        }
      }
    }
  }
}