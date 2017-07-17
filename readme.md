# WebSSO Proof-of-Concept (PoC)

Denne PoC er lavet, for at sikre den valgte arkitektur i løsningen passer sammen med SAML2.0 WebSSO med POST bindings på et teknisk niveau. Derudover er et sekundært formål at give et simpelt eksempel på, hvordan sikkerhedsarkitekturen kan virke til brug for fælles forståelse i projektet.

## Overblik
PoC'en indeholder:
Komponent  | Fil   | Beskrivelse
---------- | ----- |------------
Service Provider | service_provider_poc.py | Et eksempel Service Provider, som udstiller en API hvorfra JSON data kan hentes.
Web-frontend Server | webapp/frontend_server_poc.py | Foobar


## Install, deploy og anvendelse

### Opsætning af egen Service Provider

## Referencer
[SAML]: [SAML 2.0](https://wiki.oasis-open.org/security/FrontPage#SAML_V2.0_Standard)
[SAML-core]: [SAML 2.0 Core](http://www.oasis-open.org/committees/download.php/56776/sstc-saml-core-errata-2.0-wd-07.pdf)
[SAML-profil]: [SAML 2.0 WebSSO Profile](http://www.oasis-open.org/committees/download.php/56782/sstc-saml-profiles-errata-2.0-wd-07.pdf)
[SAML-bindings]: [SAML 2.0 Bindings](http://www.oasis-open.org/committees/download.php/56779/sstc-saml-bindings-errata-2.0-wd-06.pdf)