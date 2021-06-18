pipeline {
    agent any
    stages {
        stage('Clean') {
            steps {
                sh "git clean -fxd"
            }
        }
        stage('Test') {
            agent {
                dockerfile {
                    args '-u root:root -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                dir("pmd") {
                    sh "pipenv sync --dev"
                    sh "pipenv run behave pmd/tests/behaviour --tags=-skip -f json -o pmd/tests/behaviour/test-results.json --junit"
                    dir("pmd/tests/unit") {
                        sh "PIPENV_PIPFILE='../../../Pipfile' pipenv run python -m xmlrunner -o reports *.py"
                    }

                    stash name: "test-results", includes: "**/test-results.json,**/reports/*.xml"
                }
            }
        }
    }
    post {
        always {
            unstash name: "test-results"
            cucumber fileIncludePattern: '**/test-results.json'
            junit allowEmptyResults: true, testResults: '**/reports/*.xml'
        }
    }
}