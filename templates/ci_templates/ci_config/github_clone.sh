'which ssh-agent || ( apt-get update -y && apt-get install openssh-client -y)'
eval $(ssh-agent -s)
mkdir -p ~/.ssh
ssh-keyscan github.com >> ~/.ssh/known_hosts
ssh-agent -a /tmp/ssh_agent.sock > /dev/null
echo "$GITHUB_PRIVATE_KEY" > ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
git config --global user.name "$GITLAB_USER_NAME"
git config --global user.email "$GITLAB_USER_EMAIL"