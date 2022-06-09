pipeline {
    agent {
        dockerfile {
            args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
            reuseNode true
        }
    }
    stages {
        stage('Clean') {
            steps {
                script {
                    // Clean up any unwanted files lying about after the previous build.
                    sh "git clean -fxd --exclude='.venv'"
                }
            }
        }
        stage('Pyright') {
            when { not { buildingTag() } }
            steps {
                sh 'poetry run pyright . --lib'    
            }
        }
        stage('Test') {
            when { not { buildingTag() } }
            steps {
                script {
                    try {
                        sh 'poetry run behave tests/behaviour --tags=-skip -f json.cucumber -o tests/behaviour/test-results.json'
                        dir('tests/unit') {
                            sh "poetry run pytest --junitxml=pytest_results_csvcubed.xml"
                        }
                    } catch (ex) {
                        echo "An error occurred when testing: ${ex}"
                        stash name: 'test-results', includes: '**/test-results.json,**/*results*.xml' // Ensure test reports are available to be reported on.
                        throw ex
                    }

                    stash name: 'test-results', includes: '**/test-results.json,**/*results*.xml' // Ensure test reports are available to be reported on.
                }
            }
        }
        stage('Tox') {
            when { 
                buildingTag()
                tag pattern: "v\\d+\\.\\d+\\.\\d+(-RC\\d)?", comparator: "REGEXP"
            }
            agent {
                docker { image 'gsscogs/pythonversiontesting' }
            }
            steps {
                script {
                    try {
                        sh 'tox'
                    } catch (ex) {
                        echo "An error occurred testing with tox: ${ex}"
                        stash name: 'tox-test-results', includes: '**/tox-test-results-*.json,**/*results*.xml'
                        throw ex
                    }
                    // Ensure test reports are available to be reported on.
                    stash name: 'tox-test-results', includes: '**/tox-test-results-*.json,**/*results*.xml'
                }
            }
        }
        stage('Package') {
            steps {
                sh 'poetry build'
                
                stash name: 'wheels', includes: '**/dist/*.whl'
            }
        }
        stage('Building Documentation') {
            steps {
                script {
                    sh "poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs csvcubed \"setup*\" \"tests\""
                    sh 'poetry run sphinx-build -W -b html docs docs/_build/html'
                    

                    dir('external-docs'){
                        sh "python3 -m mkdocs build"
                    }

                    stash name: 'docs', includes: '**/docs/_build/html/**/*'
                    stash name: 'mkdocs', includes: '**/external-docs/site/**/*'
                }
            }
        }
        stage('Publishing Documentation'){
            when {
                branch 'main'
            }
            steps{
                script{
                    try {
                        withCredentials([gitUsernamePassword(credentialsId: 'csvcubed-github', gitToolName: 'git-tool')]){
                            sh 'git clone "https://github.com/GSS-Cogs/csvcubed-docs.git"'
                            dir ('csvcubed-docs') {
                                sh 'git config --global user.email "csvcubed@gsscogs.uk" && git config --global user.name "csvcubed"'
                                
                                if (fileExists("external")) {
                                    sh 'git rm -rf external'
                                }
                                sh 'mkdir external'
                                sh 'cp -r ../external-docs/site/* external'

                                if (fileExists("api-docs")) {
                                    sh 'git rm -rf api-docs'
                                }
                                sh 'mkdir api-docs'
                                sh 'mkdir api-docs/csvcubed'

                                sh 'cp -r ../csvcubed/docs/_build/html/* api-docs/csvcubed'

                                sh 'touch .nojekyll'

                                sh 'git add *'
                                sh 'git add .nojekyll'
                                sh 'git commit -m "Updating documentation."'
                                // commit being built in csvcubed repo: https://github.com/GSS-Cogs/csvcubed
                                sh 'git checkout gh-pages'
                                sh 'git reset --hard main'
                                sh 'git push -f'
                            }
                        }
                    } finally {
                        sh 'rm -rf csvcubed-docs'
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                try {
                    unstash name: 'test-results'
                } catch (Exception e) {
                    echo 'test-results stash does not exist'
                }

                try {
                    unstash name: 'tox-test-results'
                } catch (Exception e) {
                    echo 'tox-test-results stash does not exist'
                }

                cucumber fileIncludePattern: '**/test-results.json'
                cucumber fileIncludePattern: '**/tox-test-results-*.json'
                junit allowEmptyResults: true, testResults: '**/*results*.xml'

                try {
                    unstash name: 'wheels'
                } catch (Exception e) {
                    echo 'wheels stash does not exist'
                }

                try {
                    unstash name: 'docs'
                } catch (Exception e) {
                    echo 'docs stash does not exist'
                }

                try {
                    unstash name: 'mkdocs'
                } catch (Exception e) {
                    echo 'mkdocs stash does not exist'
                }

                archiveArtifacts artifacts: '**/dist/*.whl, **/docs/_build/html/**/*, **/external-docs/site/**/*, **/test-results.json, **/tox-test-results-*.json, **/*results*.xml', fingerprint: true

                // Set more permissive permissions on all files so future processes/Jenkins can easily delete them.
                sh 'chmod -R ugo+rw .'
                // Clean up any unwanted files lying about.
                sh "git clean -fxd --exclude='.venv'"
            }
        }
    }
}
