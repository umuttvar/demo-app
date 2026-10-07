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
    - name: git
      image: alpine/git:v2.54.0
      command: ["cat"]
      tty: true
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
              --exit-code 1 \
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
    
    stage ('Update GitOps') {
      steps {
        container ('git') {
          withCredentials([usernamePassword(credentialsId: 'github-gitops' ,
                                            usernameVariable: 'GIT_USER',
                                            passwordVariable: 'GIT_TOKEN')]) {
          sh '''
            rm -rf gitops
            git clone "https://${GIT_USER}:${GIT_TOKEN}@github.com/umuttvar/homelab-k8s.git" gitops
            cd gitops

            sed -i "s|^  tag: .*|  tag: \\"${VERSION}\\"|" charts/demo-app/values.yaml
            git config user.name "Jenkins CI"
            git config user.email "jenkins@homelab.local"
            git add charts/demo-app/values.yaml
            git commit -m "demo-app: deploy ${VERSION}"
            git push origin main

          '''                                  }
        }
      }
    }
  }
}