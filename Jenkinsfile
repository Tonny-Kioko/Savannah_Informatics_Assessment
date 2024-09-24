pipeline {
    agent any

    environment {
        REGISTRY = DOCKER.REGISTRY
        REGISTRY_CREDENTIALS = DOCKER.CREDENTIALS
        DOCKER_IMAGE = 'savannah_web'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git 'hhttps://github.com/Tonny-Kioko/Savannah_Informatics_Assessment.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}")
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh 'python manage.py test core.test'
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('', "${REGISTRY_CREDENTIALS}") {
                        dockerImage.push("${env.BUILD_NUMBER}")
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(['ec2-key-pair']) {
                    sh '''
                    ssh -o StrictHostKeyChecking=no ec2-user@<EC2_IP> 'cd /savannah && docker-compose down && git pull && docker-compose up -d'
                    '''
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
