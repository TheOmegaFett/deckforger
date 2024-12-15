Search.setIndex({"alltitles": {"Application Setup": [[2, null]], "CLI Controller": [[0, "cli-controller"]], "Card": [[3, "card"]], "Card Controller": [[0, "card-controller"]], "Card Schema": [[4, "module-schemas.card_schema"]], "CardSet": [[3, "cardset"]], "CardSet Schema": [[4, "module-schemas.cardset_schema"]], "Contents:": [[1, null]], "Controllers": [[0, null]], "Database Configuration": [[2, "database-configuration"]], "Deck": [[3, "deck"]], "Deck Controller": [[0, "deck-controller"]], "Deck Schema": [[4, "module-schemas.deck_schema"]], "DeckBox Controller": [[0, "deckbox-controller"]], "DeckBox Schema": [[4, "module-schemas.deckbox_schema"]], "DeckCard": [[3, "deckcard"]], "DeckCard Schema": [[4, "module-schemas.deckcard_schema"]], "Deckforger documentation": [[1, null]], "Format": [[3, "format"]], "Format Controller": [[0, "format-controller"]], "Format Schema": [[4, "module-schemas.format_schema"]], "Models": [[3, null]], "Schemas": [[4, null]]}, "docnames": ["controllers", "index", "init", "models", "schemas"], "envversion": {"sphinx": 64, "sphinx.domains.c": 3, "sphinx.domains.changeset": 1, "sphinx.domains.citation": 1, "sphinx.domains.cpp": 9, "sphinx.domains.index": 1, "sphinx.domains.javascript": 3, "sphinx.domains.math": 2, "sphinx.domains.python": 4, "sphinx.domains.rst": 2, "sphinx.domains.std": 2, "sphinx.ext.viewcode": 1}, "filenames": ["controllers.rst", "index.rst", "init.rst", "models.rst", "schemas.rst"], "indexentries": {"init": [[2, "module-init", false]], "module": [[2, "module-init", false]]}, "objects": {"": [[2, 0, 0, "-", "init"]], "controllers": [[0, 0, 0, "-", "card_controller"], [0, 0, 0, "-", "cli_controller"], [0, 0, 0, "-", "deck_controller"], [0, 0, 0, "-", "deckbox_controller"], [0, 0, 0, "-", "format_controller"]], "controllers.card_controller": [[0, 1, 1, "", "create_card"], [0, 1, 1, "", "delete_card"], [0, 1, 1, "", "get_all_cards"], [0, 1, 1, "", "get_one_card"], [0, 1, 1, "", "search_cards"], [0, 1, 1, "", "update_card"], [0, 1, 1, "", "validate_name"], [0, 1, 1, "", "validate_set_id"], [0, 1, 1, "", "validate_type"]], "controllers.cli_controller": [[0, 1, 1, "", "cleanup_database"], [0, 1, 1, "", "create_tables"], [0, 1, 1, "", "drop_tables"], [0, 1, 1, "", "health_check"], [0, 1, 1, "", "list_routes"], [0, 1, 1, "", "seed_tables"]], "controllers.deck_controller": [[0, 1, 1, "", "create_deck"], [0, 1, 1, "", "update_deck"], [0, 1, 1, "", "validate_deck"], [0, 1, 1, "", "validate_deck_rules"]], "controllers.deckbox_controller": [[0, 1, 1, "", "add_deck_to_deckbox"], [0, 1, 1, "", "create_deckbox"], [0, 1, 1, "", "delete_deckbox"], [0, 1, 1, "", "read_all_deckboxes"], [0, 1, 1, "", "read_one_deckbox"], [0, 1, 1, "", "remove_deck_from_deckbox"], [0, 1, 1, "", "show_decks_in_deckbox"], [0, 1, 1, "", "update_deckbox"], [0, 1, 1, "", "validate_name"]], "controllers.format_controller": [[0, 1, 1, "", "create_format"], [0, 1, 1, "", "delete_format"], [0, 1, 1, "", "get_format"], [0, 1, 1, "", "get_formats"], [0, 1, 1, "", "update_format"], [0, 1, 1, "", "validate_deck_format"]], "models": [[3, 0, 0, "-", "Card"], [3, 0, 0, "-", "CardSet"], [3, 0, 0, "-", "Deck"], [3, 0, 0, "-", "DeckBox"], [3, 0, 0, "-", "DeckCard"], [3, 0, 0, "-", "format"]], "models.Card": [[3, 2, 1, "", "decks"], [3, 2, 1, "", "id"], [3, 2, 1, "", "name"], [3, 2, 1, "", "set"], [3, 2, 1, "", "set_id"], [3, 2, 1, "", "type"]], "models.CardSet": [[3, 2, 1, "", "cards"], [3, 2, 1, "", "description"], [3, 2, 1, "", "id"], [3, 2, 1, "", "name"], [3, 2, 1, "", "release_date"]], "models.Deck": [[3, 2, 1, "", "created_at"], [3, 2, 1, "", "deck_cards"], [3, 2, 1, "", "deckbox"], [3, 2, 1, "", "deckbox_id"], [3, 2, 1, "", "description"], [3, 2, 1, "", "format_id"], [3, 2, 1, "", "id"], [3, 2, 1, "", "name"], [3, 2, 1, "", "ratings"], [3, 2, 1, "", "updated_at"]], "models.DeckBox": [[3, 2, 1, "", "decks"], [3, 2, 1, "", "description"], [3, 2, 1, "", "id"], [3, 2, 1, "", "name"]], "models.DeckCard": [[3, 2, 1, "", "card_id"], [3, 2, 1, "", "deck_id"], [3, 2, 1, "", "id"], [3, 2, 1, "", "quantity"]], "models.format": [[3, 3, 1, "", "Format"]], "models.format.Format": [[3, 2, 1, "", "description"], [3, 2, 1, "", "id"], [3, 2, 1, "", "name"]], "schemas": [[4, 0, 0, "-", "card_schema"], [4, 0, 0, "-", "cardset_schema"], [4, 0, 0, "-", "deck_schema"], [4, 0, 0, "-", "deckbox_schema"], [4, 0, 0, "-", "deckcard_schema"], [4, 0, 0, "-", "format_schema"]], "schemas.card_schema": [[4, 3, 1, "", "CardSchema"]], "schemas.card_schema.CardSchema": [[4, 3, 1, "", "Meta"], [4, 2, 1, "", "opts"]], "schemas.card_schema.CardSchema.Meta": [[4, 2, 1, "", "include_fk"], [4, 2, 1, "", "model"], [4, 2, 1, "", "sqla_session"]], "schemas.cardset_schema": [[4, 3, 1, "", "SetSchema"]], "schemas.cardset_schema.SetSchema": [[4, 3, 1, "", "Meta"], [4, 2, 1, "", "cards"], [4, 2, 1, "", "description"], [4, 2, 1, "", "id"], [4, 2, 1, "", "name"], [4, 2, 1, "", "opts"], [4, 2, 1, "", "release_date"]], "schemas.cardset_schema.SetSchema.Meta": [[4, 2, 1, "", "load_instance"], [4, 2, 1, "", "model"], [4, 2, 1, "", "sqla_session"]], "schemas.deck_schema": [[4, 3, 1, "", "DeckSchema"]], "schemas.deck_schema.DeckSchema": [[4, 3, 1, "", "Meta"], [4, 2, 1, "", "cards"], [4, 2, 1, "", "created_at"], [4, 2, 1, "", "deckbox"], [4, 2, 1, "", "description"], [4, 2, 1, "", "format_id"], [4, 2, 1, "", "id"], [4, 2, 1, "", "name"], [4, 2, 1, "", "opts"], [4, 2, 1, "", "ratings"], [4, 2, 1, "", "updated_at"]], "schemas.deck_schema.DeckSchema.Meta": [[4, 2, 1, "", "model"], [4, 2, 1, "", "sqla_session"]], "schemas.deckbox_schema": [[4, 3, 1, "", "DeckBoxSchema"]], "schemas.deckbox_schema.DeckBoxSchema": [[4, 3, 1, "", "Meta"], [4, 2, 1, "", "decks"], [4, 2, 1, "", "description"], [4, 2, 1, "", "id"], [4, 2, 1, "", "name"], [4, 2, 1, "", "opts"]], "schemas.deckbox_schema.DeckBoxSchema.Meta": [[4, 2, 1, "", "model"], [4, 2, 1, "", "sqla_session"]], "schemas.deckcard_schema": [[4, 3, 1, "", "DeckCardSchema"]], "schemas.deckcard_schema.DeckCardSchema": [[4, 3, 1, "", "Meta"], [4, 2, 1, "", "card"], [4, 2, 1, "", "card_id"], [4, 2, 1, "", "deck"], [4, 2, 1, "", "deck_id"], [4, 2, 1, "", "id"], [4, 2, 1, "", "opts"], [4, 2, 1, "", "quantity"]], "schemas.deckcard_schema.DeckCardSchema.Meta": [[4, 2, 1, "", "model"], [4, 2, 1, "", "sqla_session"]], "schemas.format_schema": [[4, 3, 1, "", "FormatSchema"]], "schemas.format_schema.FormatSchema": [[4, 3, 1, "", "Meta"], [4, 2, 1, "", "description"], [4, 2, 1, "", "id"], [4, 2, 1, "", "name"], [4, 2, 1, "", "opts"]], "schemas.format_schema.FormatSchema.Meta": [[4, 2, 1, "", "model"], [4, 2, 1, "", "sqla_session"]]}, "objnames": {"0": ["py", "module", "Python module"], "1": ["py", "function", "Python function"], "2": ["py", "attribute", "Python attribute"], "3": ["py", "class", "Python class"]}, "objtypes": {"0": "py:module", "1": "py:function", "2": "py:attribute", "3": "py:class"}, "terms": {"": 0, "200": 0, "201": 0, "400": 0, "404": 0, "409": 0, "500": 0, "A": 3, "If": 0, "about": 3, "ad": 0, "add": 0, "add_deck_to_deckbox": 0, "against": 0, "alia": 4, "all": [0, 3], "allow": [0, 3], "alreadi": 0, "an": 0, "ani": 0, "api": 0, "applic": 1, "ar": 3, "arg": 4, "associ": [3, 4], "avail": 0, "base": [3, 4], "being": 3, "belong": 0, "between": 3, "black": 3, "bodi": 0, "box": [0, 3, 4], "card": 1, "card_control": 0, "card_id": [0, 3, 4], "card_schema": 4, "cardschema": 4, "cardset": 1, "cardset_schema": 4, "check": 0, "class": [3, 4], "clean": 0, "cleanup": 0, "cleanup_databas": 0, "cli": 1, "cli_control": 0, "complet": 0, "composit": 0, "configur": 1, "contain": [0, 3], "control": 1, "copi": [3, 4], "count": 0, "creat": 0, "create_card": 0, "create_deck": 0, "create_deckbox": 0, "create_format": 0, "create_t": 0, "created_at": [3, 4], "creation": [3, 4], "data": 0, "databas": [0, 1, 3], "date": [3, 4], "datetim": 3, "deck": 1, "deck_card": 3, "deck_control": 0, "deck_id": [0, 3, 4], "deck_schema": 4, "deckbox": [1, 3], "deckbox_control": 0, "deckbox_id": [0, 3], "deckbox_schema": 4, "deckboxschema": 4, "deckcard": 1, "deckcard_schema": 4, "deckcardschema": 4, "deckforg": 2, "deckschema": 4, "defin": 3, "delet": 0, "delete_card": 0, "delete_deckbox": 0, "delete_format": 0, "descript": [0, 3, 4], "deseri": [2, 4], "detail": [0, 3], "differ": 3, "drop": 0, "drop_tabl": 0, "dummysess": 4, "duplic": 0, "e": 3, "each": 3, "empti": 0, "energi": 3, "entri": 0, "error": 0, "etc": 0, "exampl": 3, "exist": 0, "expand": 3, "extens": 2, "factori": [], "fail": 0, "field": 0, "filter": 0, "fire": 0, "flask": 2, "flask_marshmallow": 4, "follow": 0, "foreign": 3, "format": 1, "format_control": 0, "format_id": [0, 3, 4], "format_schema": 4, "formatschema": 4, "forward": 3, "found": 0, "from": 0, "g": 3, "game": [0, 3, 4], "get_all_card": 0, "get_format": 0, "get_one_card": 0, "grass": 0, "ha": 3, "health": 0, "health_check": 0, "i": 0, "id": [0, 3, 4], "identifi": [3, 4], "includ": 3, "include_fk": 4, "initi": [0, 2], "input": 0, "int": [0, 3], "invalid": 0, "item": 0, "kei": 3, "kwarg": [3, 4], "last": [3, 4], "legal": [0, 3], "length": 0, "like": 3, "list": 0, "list_rout": 0, "load_inst": 4, "long": 0, "manag": [0, 3], "mani": 3, "marshmallow": 2, "match": 0, "meta": 4, "method": 0, "migrat": 2, "miss": 0, "model": [1, 4], "modul": [2, 3], "multipl": 3, "must": 3, "name": [0, 3, 4], "nest": 4, "new": 0, "newest": 3, "number": [3, 4], "object": 4, "onli": 3, "oper": [0, 2], "opt": 4, "option": 0, "paramet": 0, "parent": [3, 4], "plai": 3, "pokemon": [0, 3, 4], "pok\u00e9mon": 3, "posit": 0, "primari": 3, "quantiti": [3, 4], "rais": 0, "rate": [3, 4], "read_all_deckbox": 0, "read_one_deckbox": 0, "refer": [3, 4], "regist": 0, "relationship": [3, 4], "releas": [3, 4], "release_d": [3, 4], "remov": 0, "remove_deck_from_deckbox": 0, "repres": 3, "request": 0, "requir": 0, "restrict": 3, "retriev": 0, "return": 0, "rout": 0, "rule": [0, 3, 4], "run": 0, "same": 0, "schema": 1, "schemaopt": 4, "search": 0, "search_card": 0, "seed": 0, "seed_tabl": 0, "self": 0, "serial": [2, 4], "set": [0, 2, 3, 4], "set_id": [0, 3], "setschema": 4, "setup": 1, "show_decks_in_deckbox": 0, "sourc": [0, 3, 4], "specif": [0, 3], "sqla": 4, "sqla_sess": 4, "sqlalchemi": 2, "sqlalchemyschema": 4, "sqlalchemyschemaopt": 4, "standard": 3, "statu": 0, "storag": 3, "store": [3, 4], "str": [0, 3], "successfulli": 0, "tabl": 0, "tcg": [0, 3, 4], "text": 3, "thi": [0, 2, 3], "timestamp": [3, 4], "too": 0, "tournament": 3, "track": 3, "trade": 3, "trainer": 3, "true": 4, "type": [0, 3], "uniqu": 3, "unlimit": 3, "up": [0, 2], "updat": [0, 3, 4], "update_card": 0, "update_deck": 0, "update_deckbox": 0, "update_format": 0, "updated_at": [3, 4], "us": 0, "valid": 0, "validate_deck": 0, "validate_deck_format": 0, "validate_deck_rul": 0, "validate_nam": 0, "validate_set_id": 0, "validate_typ": 0, "validationerror": 0, "valu": 0, "violat": 0, "water": 0, "which": 3, "white": 3}, "titles": ["Controllers", "Deckforger documentation", "Application Setup", "Models", "Schemas"], "titleterms": {"applic": 2, "card": [0, 3, 4], "cardset": [3, 4], "cli": 0, "configur": 2, "content": 1, "control": 0, "databas": 2, "deck": [0, 3, 4], "deckbox": [0, 4], "deckcard": [3, 4], "deckforg": 1, "document": 1, "factori": [], "format": [0, 3, 4], "model": 3, "schema": 4, "setup": 2}})