pipeline {
    agent any
      environment {
    DOCKERHUB_CREDENTIALS = credentials('dockerhub')
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
                    docker.withRegistry(DOCKER_REGISTRY_URL, DOCKERHUB_CREDENTIALS) {
                        def registry = docker.getRegistry()
                        echo "Connected to Docker registry: ${registry.url}"
                    }
                }
            }
        }

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
