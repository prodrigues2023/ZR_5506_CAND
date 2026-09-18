pipeline {
    agent any

    stages {
        stage('Quality checks') {
            steps {
                sh 'cd backend && uv run ruff check app migrations tests && uv run pytest'
                sh 'cd frontend && npm ci && npm run build'
            }
        }

        stage('Build and smoke test') {
            steps {
                withCredentials([
                    string(credentialsId: 'series-huggingface-api-key', variable: 'HF_API_KEY'),
                    usernamePassword(
                        credentialsId: 'series-postgres',
                        usernameVariable: 'DB_USER',
                        passwordVariable: 'DB_PASSWORD'
                    )
                ]) {
                    sh '''
                        export POSTGRES_DB=series
                        export POSTGRES_USER="$DB_USER"
                        export POSTGRES_PASSWORD="$DB_PASSWORD"
                        export SERIES_DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/${POSTGRES_DB}"
                        export SERIES_HUGGINGFACE_API_KEY="$HF_API_KEY"
                        docker compose build --no-cache && docker compose up -d
                        curl --fail http://localhost:7777/api/health
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker compose down'
        }
    }
}
