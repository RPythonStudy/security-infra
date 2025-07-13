# pseudonymize 키/값(Read Only)만 접근 가능
path "pseudonymize/data/ff3" {
  capabilities = ["read"]
}

# KV v2 metadata도 조회 가능 (선택)
path "pseudonymize/metadata/ff3" {
  capabilities = ["read"]
}
