MAPPING_GENRES = {
    "mappings": {
        "properties": {
            "id": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256,
                    }
                }
            },
            "name": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256,
                    }
                }
            }
        }
    }
}
