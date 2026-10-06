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
    - name: trivy
      image: aquasec/trivy:0.75.0
      command: ["cat"]
      tty: true
    - name: crane
      image: gcr.io/go-containerregistry/crane:debug
      command: ["/busybox/cat"]
      tty: true
      env:
        - name: DOCKER_CONFIG
          value: /docker-config
      volumeMounts:
        - name: docker-config
          mountPath: /docker-config
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

    stage('Build') {
      steps {
        container('kaniko') {
          sh '''
            /kaniko/executor \
              --context="$WORKSPACE" \
              --dockerfile="$WORKSPACE/Dockerfile" \
              --build-arg APP_VERSION="$VERSION" \
              --destination="$IMAGE:$VERSION" \
              --no-push \
              --tar-path="$WORKSPACE/image.tar"
          '''
        }
      }
    }

    stage('Security Scan') {
      steps {
        container('trivy') {
          sh '''
            trivy image \
              --input "$WORKSPACE/image.tar" \
              --severity HIGH,CRITICAL \
              --ignore-unfixed \
              --exit-code 0 \
              --no-progress
          '''
        }
      }
    }

    stage('Push') {
      steps {
        container('crane') {
          sh 'crane push "$WORKSPACE/image.tar" "$IMAGE:$VERSION"'
        }
      }
    }
  }
}