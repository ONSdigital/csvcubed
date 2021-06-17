pipeline {
    agent any
    stages {
        stage('Test') {
            agent {
                dockerfile {
                    args '-u root:root -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                dir("pmd") {
                    sh "pipenv sync --dev"
                    sh "pipenv run behave pmd/tests/behaviour --tags=-skip -f json -o test-results.json --junit"
                    cucumber 'pmd/test-results.json'
                    junit allowEmptyResults: true, testResults: 'pmd/reports/*.xml'
                }
            }
        }
    }
}