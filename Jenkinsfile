pipeline {
  agent {
    kubernetes {
      yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: python
      image: python:3.13-slim
      command: ["sleep"]
      args: ["infinity"]
'''
    }
  }

  triggers {
    pollSCM('H/5 * * * *')
  }

  stages {
    stage('Test') {
      steps {
        container('python') {
          sh 'pip install --no-cache-dir -r requirements-dev.txt'
          sh 'python -m pytest -v'
        }
      }
    }
  }
}