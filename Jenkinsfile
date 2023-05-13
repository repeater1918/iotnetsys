pipeline {
    agent any

    environment {
        DOCKERHUB = credentials('dockerhub')
    }

    stages {
        stage('Checkout') {
            agent { label 'linux-docker' }
            steps {
                checkout scmGit(branches: [[name: '*/development']], userRemoteConfigs: [[credentialsId: 'github-syd', url: 'git@github.sydney.edu.au:jomc7031/CS44-2-IOTNetSys.git']])
                sh 'ls'
            }
        }

        stage('Setup') {
            agent { label 'linux-docker' }
            steps {
                withCredentials([file(credentialsId: 'mongo-envs', variable: 'ENV_FILE')]) {
                    script {
                        def secretsContent = readFile("${ENV_FILE}")
                        def secrets = secretsContent.split('\n').collectEntries {
                            def (k, v) = it.split('=')
                            [(k): v]
                        }
                        secrets.each { k, v ->
                            env."${k}" = v
                        }

                        sh 'cat docker-compose.yaml | envsubst > docker-compose.env.yaml'
                        sh 'cat docker-compose.env.yaml'
                    }
                }

            }

        }

        stage('Build Image') {
            agent { label 'linux-docker' }
            steps {
                withCredentials([file(credentialsId: 'mongo-envs', variable: 'ENV_FILE')]) {
                    sh "sed -i 's|.envs/mongodb.env|${ENV_FILE}|g' docker-compose.yaml"
                    sh "echo $DOCKERHUB_PSW | sudo docker login -u $DOCKERHUB_USR --password-stdin"
                    sh 'sudo docker-compose build'
                }
            }
        }

        stage('Publish') {
            agent { label 'linux-docker' }
            steps {
                sh 'sudo docker push repeater918/iontnetsys-aap:latest'
                sh 'sudo docker push repeater918/iontnetsys-aas:latest'
                sh 'sudo docker push repeater918/iontnetsys-proxy:latest'
            }
        }

        stage('Deploy') {
            agent { label 'linux-docker' }
            steps {
                    sshagent(['iotnetsys']) {
                        sh 'scp -o StrictHostKeyChecking=no ./docker-compose.env.yaml ec2-user@ec2-54-252-240-175.ap-southeast-2.compute.amazonaws.com:/home/ec2-user/app/docker-compose.yaml'
                        sh 'ssh -tt ec2-user@ec2-54-252-240-175.ap-southeast-2.compute.amazonaws.com -o StrictHostKeyChecking=no "echo $DOCKERHUB_PSW | sudo docker login -u $DOCKERHUB_USR --password-stdin; cd /home/ec2-user/app/; sudo docker-compose pull; exit"'
                        sh 'ssh -tt ec2-user@ec2-54-252-240-175.ap-southeast-2.compute.amazonaws.com -o StrictHostKeyChecking=no "cd /home/ec2-user/app/; sudo docker-compose up -d --no-build; exit"'
                    }
            }
        }
    }
}
