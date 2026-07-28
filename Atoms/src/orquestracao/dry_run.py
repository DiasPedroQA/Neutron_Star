def is_dry_run(options: dict) -> bool:
    # Espera uma chave 'dry_run' booleana; função simples e testável
    return bool(options.get("dry_run"))
