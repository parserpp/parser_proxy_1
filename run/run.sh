_token=$(echo ${GITHUB_TOKEN})
curl -X POST https://api.github.com/repos/parserpp/parser_proxy_poll/dispatches \
    -H "Accept: application/vnd.github.everest-preview+json" \
    -H "Authorization: token ${_token}" \
    --data '{"event_type": "webhook-1"}'