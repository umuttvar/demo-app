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
    - name: kaniko
      image: gcr.io/kaniko-project/executor:debug
      command: ["/busybox/cat"]
      tty: true
      volumeMounts:
        - name: docker-config
          mountPath: /kaniko/.docker
  volumes:
    - name: docker-config
      secret:
        secretName: ghcr-creds
        items:
          - key: .dockerconfigjson
            path: config.json
'''
    }
  }

  environment {
    IMAGE = 'ghcr.io/umuttvar/demo-app'
    VERSION = "1.0.${BUILD_NUMBER}"
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

    stage('Build & Push') {
      steps {
        container('kaniko') {
          sh '''
            /kaniko/executor \
              --context="$WORKSPACE" \
              --dockerfile="$WORKSPACE/Dockerfile" \
              --build-arg APP_VERSION="$VERSION" \
              --destination="$IMAGE:$VERSION"
          '''
        }
      }
    }
  }
}