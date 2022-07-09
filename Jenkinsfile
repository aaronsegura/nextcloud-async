pipeline {
  agent any

  stages {

    stage('Install Package') {
      steps {
        withPythonEnv('python3.10') {
          sh 'python3.10 -mpip install .'
        }
      }
    }

    stage('Run Source Code Tests') {
      parallel {
        stage('flake8 check') {
          agent {
            dockerfile {
              dir '.jenkins'
              filename 'Dockerfile-flake8'
            }
          }
          steps {
            withPythonEnv('python3.10') {
              sh 'python3.10 -mpip install --target ${WORKSPACE} flake8'
              sh 'flake8 --exclude .git,__pycache__,node_modules,.pyenv* --count --statistics --ignore E227 /data'
            }
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
            sh 'pydocstyle --convention=pep257 --count nextcloud_async || true'
            sh 'docstr-coverage -P -m nextcloud_async'
          }
        }
        stage('Unit testing') {
          steps {
            withPythonEnv('python3.10') {
              sh 'python3.10 -m unittest'
            }
          }
        }
      }
    }
  }
}