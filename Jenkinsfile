pipeline {
    agent any
      environment {
    CRED = credentials('dockerhub-cred')
    DOCKER_REGISTRY_URL = 'hub.docker.com'
    DOCKER_COMPOSE_FILE = 'docker-compose.yaml'
  }
    options {
        buildDiscarder(logRotator(daysToKeepStr: '10', numToKeepStr: '10'))
        timeout(time: 12, unit: 'HOURS')
    }

    stages {

        stage("Test Docker registry connection") {
            steps {
                script {
                    sh 'docker-compose build'
                }
                }
            }
        }

}

