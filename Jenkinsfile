pipeline {
    agent any
      environment {
    DOCKERHUB_CREDENTIALS = credentials('a2f94dce-1b5e-41ae-9291-b762e690990c')
    DOCKER_REGISTRY_URL = 'https://hub.docker.com/'
    DOCKER_COMPOSE_FILE = 'docker-compose.yaml'
  }
    options {
        buildDiscarder(logRotator(daysToKeepStr: '10', numToKeepStr: '10'))
        timeout(time: 12, unit: 'HOURS')
    }

    stages {
        stage('Build Docker images') {
        steps {
            script {
            docker.withRegistry(DOCKER_REGISTRY_URL, DOCKERHUB_CREDENTIALS) {
                def compose = docker.buildComposeFile("Build Docker Images", DOCKER_COMPOSE_FILE, "build")
                compose.images().each {
                    dockerImage.push()
                }
            }
            }
        }
        }
    }
}
