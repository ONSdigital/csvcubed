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
                    // Clean up any files lying about after the previous build. Jenkins has trouble deleting files given that our containers run as root.
                    sh "git clean -fxd" 

                    dir("devtools") {
                        sh "PIPENV_VENV_IN_PROJECT=true pipenv sync --dev"
                    }

                    dir("sharedmodels") {
                        sh "PIPENV_VENV_IN_PROJECT=true pipenv sync --dev"
                    }

                    dir("pmd") {
                        sh "PIPENV_VENV_IN_PROJECT=true pipenv sync --dev"
                        // Patch behave so that it can output the correct format for the Jenkins cucumber tool.
                        def venv_location = sh script: "pipenv --venv", returnStdout: true
                        venv_location = venv_location.trim()
                        sh "patch -d \"${venv_location}/lib/python3.9/site-packages/behave/formatter\" -p1 < /cucumber-format.patch"
                    }

                    dir("csvqb") {
                        sh "PIPENV_VENV_IN_PROJECT=true pipenv sync --dev"
                        // Patch behave so that it can output the correct format for the Jenkins cucumber tool.
                        def venv_location = sh script: "pipenv --venv", returnStdout: true
                        venv_location = venv_location.trim()
                        sh "patch -d \"${venv_location}/lib/python3.9/site-packages/behave/formatter\" -p1 < /cucumber-format.patch"
                    }
                }
            }
        }
        stage('Pyright') {
            agent {
                dockerfile {
                    args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
                    reuseNode true
                }
            }
            steps {
                    dir("devtools") {
                        sh "pipenv run pyright . --lib"                       
                    }

                    dir("sharedmodels") {
                        sh "pipenv run pyright . --lib"
                    }

                    dir("pmd") {
                        sh "pipenv run pyright . --lib"
                    }

                    dir("csvqb") {
                        sh "pipenv run pyright . --lib"
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
                    sh "pipenv run behave pmd/tests/behaviour --tags=-skip -f json.cucumber -o pmd/tests/behaviour/test-results.json"
                    dir("pmd/tests/unit") {
                        sh "PIPENV_PIPFILE='../../../Pipfile' pipenv run pytest --junitxml=pytest_results_pmd.xml"
                    }
                }
                dir("csvqb") {
                    sh "pipenv run behave csvqb/tests/behaviour --tags=-skip -f json.cucumber -o csvqb/tests/behaviour/test-results.json"
                    dir("csvqb/tests/unit") {
                        sh "PIPENV_PIPFILE='../../../Pipfile' pipenv run pytest --junitxml=pytest_results_csvqb.xml"
                    }
                }

                stash name: "test-results", includes: "**/test-results.json,**/*results*.xml" // Ensure test reports are available to be reported on.
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
                dir("sharedmodels") {
                    sh "pipenv run python setup.py bdist_wheel --universal"
                }

                dir("pmd") {
                    sh "pipenv run python setup.py bdist_wheel --universal"
                }

                dir("csvqb") {
                    sh "pipenv run python setup.py bdist_wheel --universal"
                }

                stash name: "wheels", includes: "**/dist/*.whl"
            }
        }
    }
    post {
        always {
            script {
                try {
                    unstash name: "test-results"
                } catch (Exception e) {
                    echo "test-results stash does not exist"
                }


                cucumber fileIncludePattern: '**/test-results.json'
                junit allowEmptyResults: true, testResults: '**/*results*.xml'

                try {
                    unstash name: "wheels"
                } catch (Exception e) {
                    echo "wheels stash does not exist"
                }

                archiveArtifacts artifacts: '**/dist/*.whl', fingerprint: true
            }
        }
    }
}