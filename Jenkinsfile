pipeline {
    agent {
        dockerfile {
            args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
            reuseNode true
        }
    }
    stages {
        stage('Setup') {
            steps {
                script {
                    // Clean up any unwanted files lying about after the previous build.
                    sh "git clean -fxd --exclude='.venv'"

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
                        sh "patch -Nf -d \"${venv_location}/lib/python3.9/site-packages/behave/formatter\" -p1 < /cucumber-format.patch || true"
                    }

                    dir("csvqb") {
                        sh "PIPENV_VENV_IN_PROJECT=true pipenv sync --dev"
                        // Patch behave so that it can output the correct format for the Jenkins cucumber tool.
                        def venv_location = sh script: "pipenv --venv", returnStdout: true
                        venv_location = venv_location.trim()
                        sh "patch -Nf -d \"${venv_location}/lib/python3.9/site-packages/behave/formatter\" -p1 < /cucumber-format.patch || true"
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
            steps {
                dir("sharedmodels") {
                    dir("sharedmodels/tests/unit") {
                        sh "PIPENV_PIPFILE='../../../Pipfile' pipenv run pytest --junitxml=pytest_results_sharedmodels.xml"
                    }
                }
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
            steps {               
                dir("devtools") {
                    sh "pipenv run python setup.py bdist_wheel --universal"
                }

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
        stage('Documentation') {
            steps {
                script {
                    dir("devtools") {
                        sh "pipenv run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E -o docs --implicit-namespaces -o docs devtools \"setup*\""                        
                        sh "pipenv run sphinx-build -W -b html docs docs/_build/html"
                    }

                    dir("sharedmodels") {
                        sh "pipenv run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs sharedmodels \"setup*\" \"sharedmodels/scripts\" \"sharedmodels/tests\""                        
                        sh "pipenv run sphinx-build -W -b html docs docs/_build/html"
                    }

                    dir("pmd") {
                        sh "pipenv run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs  pmd \"setup*\" \"pmd/tests\""                        
                        sh "pipenv run sphinx-build -W -b html docs docs/_build/html"
                    }

                    dir("csvqb") {
                        sh "pipenv run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs csvqb \"setup*\" \"csvqb/tests\""                        
                        sh "pipenv run sphinx-build -W -b html docs docs/_build/html"
                    }
                    
                    stash name: "docs", includes: "**/docs/_build/html/**/*"
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
                    echo "test-results stash does not exist"
                }

                cucumber fileIncludePattern: '**/test-results.json'
                junit allowEmptyResults: true, testResults: '**/*results*.xml'

                try {
                    unstash name: "wheels"
                } catch (Exception e) {
                    echo "wheels stash does not exist"
                }

                try {
                    unstash name: "docs"
                } catch (Exception e) {
                    echo "docs stash does not exist"
                }

                archiveArtifacts artifacts: '**/dist/*.whl, **/docs/_build/html/**/*', fingerprint: true

                // Set more permissive permissions on all files so future processes/Jenkins can easily delete them.
                sh 'chmod -R ugo+rw .'
                // Clean up any unwanted files lying about.
                sh "git clean -fxd --exclude='.venv'"
            }
        }
    }
}