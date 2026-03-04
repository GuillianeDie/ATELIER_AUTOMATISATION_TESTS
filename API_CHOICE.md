# API Choice

- Étudiant : Guilliane DIEPPOIS
- API choisie : Open-Meteo
- URL base : https://api.open-meteo.com/v1/
- Documentation officielle / README : https://open-meteo.com/en/docs
- Auth : None
- Endpoints testés :
  - GET /v1/forecast
  - GET ...
- Hypothèses de contrat (champs attendus, types, codes) : reponse attendu = HTTP 200
- Limites / rate limiting connu : Limite a 10 000 requete par jour
- Risques (instabilité, downtime, CORS, etc.) : risque de surcharge
