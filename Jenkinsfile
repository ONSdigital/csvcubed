pipeline {
    agent any
    stages {
        stage('Setup') {
            agent {
                dockerfile {
                    args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
                    reuseNode true
                }
            }
            steps {
                script {
                    dir("pmd") {
                        sh "pipenv sync --dev"
                        // Patch behave so that it can output the correct format for the Jenkins cucumber tool.
                        def venv_location = sh "pipenv --venv", returnStdout: true
                        sh "patch -d \"${venv_location}/lib/python3.9/site-packages/behave/formatter\" -p1 < /cucumber-format.patch"

                        stash name: "pmd-venv", includes: "${venv_location}/**/*"
                    }
                }
            }
        }
        stage('Test') {
            agent {
                dockerfile {
                    args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
                    reuseNode true
                }
            }
            steps {
                dir("pmd") {
                    unstash name: "pmd-venv"

                    sh "pipenv run behave pmd/tests/behaviour --tags=-skip -f json.cucumber -o pmd/tests/behaviour/test-results.json"
                    dir("pmd/tests/unit") {
                        sh "PIPENV_PIPFILE='../../../Pipfile' pipenv run python -m xmlrunner -o reports *.py"
                    }

                }

                stash name: "test-results", includes: "**/test-results.json,**/reports/*.xml" // Ensure test reports are available to be reported on.
            }
        }
        stage('Package') {
            agent {
                dockerfile {
                    args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
                    reuseNode true
                }
            }
            steps {               
                dir("pmd") {
                    unstash name: "pmd-venv"

                    sh "pipenv run python setup.py bdist_wheel --universal"
                    archiveArtifacts artifacts: 'dist/*.whl', fingerprint: true
                }
            }
        }
    }
    post {
        always {
            script {
                try {
                    unstash name: "test-results"
                } catch (Exception e) {
                    echo "Stash does not exist"
                }
                cucumber fileIncludePattern: '**/test-results.json'
                junit allowEmptyResults: true, testResults: '**/reports/*.xml'
            }
        }
        cleanup {
            agent {
                dockerfile {
                    args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
                    reuseNode true
                }
            }
            steps {
                // remove everything before next build (we have permissions problems since this stage is run as root)
                sh "rm -rf *" 
            }
        }
    }
}