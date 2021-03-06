# WebSSO Proof-of-Concept (PoC)

## Indhold
- [Indledning](#indled)
- [Sikkerhedsmodel i Service Provider](#sikkerhedsmodel)
- [Overblik over eksempel kode](#overblik)
- [Installation, deploy og anvendelse](#deploy)
- [Gennemgang af relevante tekniske implementationsdetaljer](#tekniskedetaljer)
- [Referencer](#referencer)
- [10 second guide til installation af Python og dependencies](#deps)

## Indledning <a name="indled"></a>
WebSSO POC'en er et konkret eksemple på implementering af SAML 2.0's WebSSO Profile (med HTTP POST binding) i et setup med en client-side application. At der er tale om en client-side application (dvs. API kald sker fra brugerens browser) giver et ekstra led i hele authentifikations flowet (mere herom senere).

Med PoC'en kan man gennemføre et end-to-end scenarie, der består i at åben webklienten i en browser, klient henter data fra API'et, blive omstillet til IdP og gennemføre login. Efter login sendes brugeren tilbage til webklienten og data kan hentes fra API, som vises i webklient.

Højniveau arkitekturen ser ud som på figuren nedenfor.
![](https://raw.githubusercontent.com/Msurrow/websso-poc/master/graphics/WebSSO%20PoC%20-%20hoejniveau.png "Højniveau illustration af sikkerhedsarkitektur")

PoC'en er udelukkende tænkt til at illustrere, hvordan flow'et i sikkerhedsmodellen er, og illustrere et end-to-end eksempel på, hvordan SAML WebSSO profilen kan implementeres. Der er derfor flere dele af implementationen, der ikke er relevant for sikkerhedsmodellen der er "faket" og som på ingen måde skal ses som eksempel på, hvordan god sikkerhed implementeres.

PoC er bygget som eksempel implementation af følgende SAML 2.0 standarder:

- I [[SAML-core]](#referencer) er ```SAML AuthnRequest``` og ```SAML Assertion``` defineret. Disse er hhv. sendt som del af et ```SAML Request``` eller et ```SAML Response```. SAML standarderne beskriver regler for både udformning og processering af autnnrequest/assertion og request/response.
    - ```SAML Request``` beskrives i [[SAML-core]](#referencer) afsnit 3.2
    - ```SAML AuthnRequest``` beskrives i [[SAML-core]](#referencer) afsnit 3.4
    - ```SAML Response``` beskrives i [[SAML-core]](#referencer) afsnit 3.2
    - ```SAML Assertion``` beskrives i [[SAML-core]](#referencer) afsnit 2
- I [[SAML-profil]](#referencer) er SAML WebSSO Profile profilen beskrevet. Profilen er det centrale element, som beskriver hvordan sikkerhedsmodellen og integrationen med IdP'er virker.
    - WebSSO Profile beskrives i [[SAML-profil]](#referencer) afsnit 4.1
- I [[SAML-bindings]](#referencer) er beskrevet hvordan WebSSO profilen kan implementeres via HTTP. Dvs. det er en beskrivelse af, hvordan beskeder udvæksles via HTTP. Der er flere muligheder ("bindings"). Denne PoC bygge på SAML HTTP POST bindings.
    - HTTP POST Binding beskrives i [[SAML-bindings]](#referencer) afsnit 3.5
- I [[SAML-technical overview]](#referencer) er beskrivelser af, hvordan WebSSO profilen implementeres på et mere konkret (teknisk) niveau, end i ovenstående dokumenter.

## Sikkerhedsmodel i Service Provider<a name="sikkerhedsmodel"></a>
**Nedenstående udgør et _eksempel_ på, hvordan sikkerhedsmodellen i Service Provideren _kan_ implementeres. Til løsningen skal vælges den implementering der passer bedst til løsningen og projektet.**

```service_provider_poc.py``` udgør i denne PoC Service Provideren og requests til API endpoints kræver at request'eren har autentificeret sig overfor Service Provider. Autentifikationen sker ved brug af SAML WebSSO profil (se [[SAML-profile]](#referencer)) sammen med en "ekstern" IdP. 

WebSSO profilen resuterer i at requester'en kan præsentere en gyldig SAML Assertion for Service Provideren. Denne SAML Assertion bruger Service Provideren til at autentificere brugeren og give adgang. 

Med WebSSO profilen og HTTP POST-bindings får webklienten (client-side app'en) aldrig selve SAML Assertionen. Derfor kan denne ikke sendes med ved hvert kald til Service Providerens API endpoints.

Service Provideren væksler derfor en gylding SAML Assertion til en token (med begrænset levetid), når webklienten sender SAML Assertionen. Denne token kan inkluderes i alle efterfølgende kald til API endpoints for at sikre at request'eren er autentificeret. Dette er hvad der i SAML profilerne beskrives som at Service Provideren "har en etableret sikkerhedskontekst med Service Consumer", dvs. der er udsted en gyldig token.

Forholdene mellem komponenter kan illustreres sådan (bemærk dette er ikke det faktiske flow):
![](https://raw.githubusercontent.com/Msurrow/websso-poc/master/graphics/WebSSO%20PoC%20-%20alle%20steps.png "Alle steps i integrationsflowet")

#### Hvorfor skal RelayState bruges?
.. og hvad skal den sidste redirect til frontend serveren til for?

Det sidste step skal til fordi vi har med en client-side applikation at gøre. Hvis vi i step 10 istedet for at returnere til frontend serveren bare returnere tokenen til browseren med en HTTP 200 OK og token i payload, vil det eneste browseren modtager være en JSON token. Dvs. ingen HTML eller Javascript blive returneret, og dermed kan klienten ikke komme videre. Brugeren vil bare se en tekststreng, der er vores token og ikke længere se klienten.

RelayState sættes til en URL, som frontend serveren udstiller, hvor frontend serveren vil returnere webklienten (præcis som i step 2), dog bare med token lagt ind i html/javascript.

På den måde har webklienten nu gennemført login flowet og er i besidelse af en gyldig token til API'et, samtidig med at webklienten er loadet. Browseren/webklienten kan nu kalde API'et med en gyldig token og får faktisk svar return.

Situationen er illustreret på figuren nedenfor.
![](https://raw.githubusercontent.com/Msurrow/websso-poc/master/graphics/WebSSO%20PoC%20-%20hvorfor%20RelayState.png)

#### Bemærkning om generering af token
En tidsbegrænset token kan genereres ved at lade token bestå af:
``` token = data ":" timestamp_udstedelse ":" signatur```

Hvor signaturen er en hash ([MAC](https://en.wikipedia.org/wiki/Message_authentication_code)) af ```data + timestamp_udstedelse```, f.eks. ```HMAC(secret_key, data ":" timestamp_udstedelse)```. 

En token kunne i JSON se ud som følger (alternativt kan token base-64 encodes og anvendes i query-string):

```
{
	"data": "fx username og roller",
	"timestamp_udstedelse": 2017-07-17T10.00.00Z,
	"hash": asd213jhg213gj1231f23hg12
}
```

Herved kan det nemt tjekkes, om en token forsat er gyldig, ved blot at se på timestamp for udstedelse + lægge ønsket levetid til og sammenligne med timestamp for "nu".
Tokenen (og timestamp) kan valideres ved at (gen)beregne hash af ```data + timestamp_udstedese``` med serverens secret\_key, da secret\_key er krævet for at lave en hash med et timestamp, der er forskellige fra det, der var i den originale token udstedt af serveren. Hvis en adversary forsøger at ændre ved tokens levetid (timestamp) eller data (fx username,roller m.v.) vil den genberegnede hash ikke stemme med hash'en i tokenen. 

Token kan i princippet også være SAML Assertion, eller del heraf, så længe dennes validitet kan testes (herunder levetid). Derudover bør performance tages i betragtning i forhold til validering af SAML Response signatur. 

#### CORS
Med POST bindings [[SAML-bindings]](#referencer) returnere Service Provider en XHTML-form (se kildekode), med en Submit-knap, der sender request til IdP'en, som den kaldende javascript i webklienten kan vise til brugeren. Da request til IdP'en sker via en html-form og ikke fra javascript, rammes dette ikke af Same-Origin Policy og CORS er ikke nødvendigt.

## Overblik over eksempel kode<a name="overblik"></a>
PoC'en indeholder en API backend (Service Provider), en frontend-webserver, som server en clientside app til en browser (Service Consumer), samt nødvendig meta-data m.v. for at sætte komponenterne korrekt op.

I Service Provideren er API endpoints beskyttet og kræver at kalderen (Service Consumer) er autentificeret (detaljer [nedenfor](#sikkerhedsmodel)). Hvis der laves et API kald uden kalder er autentificeret, vil WebSSO login flowet blive sat igang.

Komponent  | Fil   | Beskrivelse
---------- | ----- |------------
Service Provider | ```service_provider_poc.py``` |En eksempel Service Provider, som udstiller en API hvorfra JSON data kan hentes.
Web-frontend Server | ```webapp/frontend_server_poc.py``` |En eksempel Web-frontend Server, som hoster en client-side app. Dvs. kald til Service Provider sker ikke fra denne komponent, med sker istedet for fra en browser.
Browser | N/A _(Lokal på PC)_ | Web-frontend Server leverer en client-side app, som afvikles i brugeren browser.
Client-side app | ```webapp/templates/index.html``` og ```webapp/static/webclient.js``` |Client-side applikationen er implementeret i disse to filer. De er alt hvad Web-frontend Serveren returnere ved et GET til den (root path '/'). 
IdP (Identity Provider) |Som test IdP anvendes [Shibboleths test IdP](https://www.testshib.org/) | Der anvendes en ekstern test IdP af to grunde: 1) Det simluere scenariet for løsningen idet IdP'en, der skal integreres til ejes af en anden organisation. 2) En veletableret test IdP sender korrekte SAML beskeder, og forventer (og validerer) korrekte SAML beskeder.

Nedenstående figur viser, hvilken af ovenstående dele af eksempel koden udgør de forskellige dele af  arkitekturen:
![](https://github.com/Msurrow/websso-poc/blob/master/graphics/WebSSO%20PoC%20-%20kode.png?raw=true "Kildekode som de hører til komponenterne")

### Teknologi
PoC'en er skrevet i Python og HTML+Javascript (jquery). Python er valgt fordi det hurtigt at lave PoCs som denne og ikke mindst fordi det er let læseligt, uanset hvilke teknologisk baggrund man kommer med.

I både ```service_provider_poc.py``` og ```frontend_server_poc.py``` er Flask mini-frameworket anvendt til at lave web-serveren. Flask er et lille og intuitivt framework, der er hurtigt at for overblik over også selvom man ikke tidligere har arbejdet med det. Mere om [Flask](http://flask.pocoo.org/).

## Install, deploy og anvendelse <a name="deploy"></a>
Der er to komponenter der skal deployes før PoC'en kan afprøves:

- ```service_provider_poc.py```
- ```frontend_server_poc.py```

### Anveldelse af service\_provider_poc.py
Med SAML POST bindings vil IdP'en efter et successfuld login, redirect browseren tilbage til Service Provideren direkte, ved at lave en HTTP POST request til Service Provideren. Derfor er det nødvendigt at vores PoC Service Provider har en public IP, som kan rammes af IdP'en. 

For nemt afprøvning af PoC'en hostes en Service Provider på Heroku. Denne Service Provider er deployet direkte fra dette GIT repo, og kildekoden du finder i repo'et her er derfor det, der kører på den Heroku-deploy'et IdP. _(NB: Eksempel Service Provideren er deployet på en gratis server og tager derfor 5-10 sek om at svare på **første** request efter 30 minutters inaktivtet)._

[Eksempel Service Provider på Heroku](http://websso-poc.herokuapp.com/)

Hvis du ønsker at prøve at deploy din egen Service Provider ud fra kode eksempler i dette repo, kan du se hvordan i afsnit nedenfor.

### Anvendelse af frontend\_server_poc.py
Start af Web-frontend Server skal blot har en port som argument

```
python webapp/frontend_server_poc.py 8000
```
Serveren startes i debug mode og findes på <http://localhost:8000/>

### Opsætning af egen Service Provider
Du kan hoste din egen Service Provider ved brug af kilekode i dette repo. Det kræver lidt opsætning og enkelte ændringer. Der er følgende ting, der skal gøres: **Bemærk(!) punkterne beskrevet herunder (eller lignende) vil skulle gøres når løsningens Service Provider skal sættes op sammen med den IdP, der skal bruges.**

- Lave metadata for din Service Provider
- Test IdP skal have importeret din Service Provider metadata
- Din Service Provider skal have "importeret" IdP metadata
- SAML AuthnRequest XML skal tilrettes
- Redirect URL til fra IdP til din Service Provider skal sættes (kræver at din Service Provider har en public IP)

#### Step 1: Lav metadata til din Service Provider
På [dette link](https://www.samltool.com/sp_metadata.php) findes et værktøj til generering af Service Provider metadata, som virker med den valgte test IdP. Følgende felter skal udfyldes:

- EntityId: En streng med navnet på din Service Provider (skal genbruges i AuthnRequest). F.eks. websso-poc.herokuapp.com
- Attribute Consume Service Endpoint (HTTP-POST): Den URL som IdP'en skal redirect til med POST request
- SP X.509 cert: Står om "optional" i metadata-værktøjet, men det er krævet for at test IdP'en vil sende et SAML Response. Dette felt skal derfor i vores PoC-case udfyldes.

Resten er ikke nødvendigt for PoC-casen. Hvordan et X.509 certifikat genereres afhænger af, hvilken platform (OS) du arbejder på, og svaret overlades derfor til google. Det kan dog siges, at det er tilstrækkeligt med et self-signet certifikat i PoC-casen.

#### Step 2: Registrer din Service Provider i IdP'en
Test Idp'en har en side til [registrering af ny service provider](https://www.testshib.org/register.html). Her kan du vælge din metadata-fil fra step 1 og importere denne.

#### Step 3: IdP Url
I din Service Provider skal IdP'en url indsættes. Dette er allerede gjort i service\_provider\poc.py. Url'en der er anvendt er

```
idp_url = "https://idp.testshib.org/idp/profile/SAML2/POST/SSO"
```

#### Step 4+5: Ret SAML AuthnRequest
I file ```helpers.py``` findes funktionen der lave AuthnRequest'et. Attributten ```AssertionConsumerServiceURL``` og elementet ```<saml:Issuer >``` skal ændres til at passe med din Service Provider (se step 1 for Issuer).

## Gennemgang af relevante tekniske implementationsdetaljer <a name="tekniskedetaljer"></a>

**Husk** at PoC'ens xml - dvs. metatada, saml requests + responses kun indeholder minimum for at eksemplet virker, og holder dermed ikke god SAML standarderne til fulde). For korrekt specifikation, herunder processerings regler, henvises til [[SAML-Core]](#referencer), [[SAML-Profiles]](#referencer), [[SAML-Bindings]](#referencer).

Først gennemgås de steder hvor relevate tekniske attributter, urls etc. sættes. Herefter gennegåes hvordan det hele kædes sammen.

### Metadata (se [```service_provider_metadata_kai_sso_poc.xml```](https://github.com/Msurrow/websso-poc/blob/master/service_provider_metadata_kai_sso_poc.xml))
I Service Provider metadata sættes to ting, der er relevante for det tekniske flow vi bygger:

- ```entityID``` sættes i ```EntityDescriptor``` elementet
- Service Provider endpoints sættes i ```AssertionConsumerService``` elementet, ```Location``` attributten

Element | Beskrivelse
------- | -----------
```entityID``` | Navn på Service Provideren. I eksemplet er websso-poc.herokuapp.com brugt
```AssertionConsumerService``` | Endpoints som IdP'en skal redirect til efter successfuld login. I eksemplet er der indsat tre, men kun <http://websso-poc.herokuapp.com/saml_login_success> anvendes.

### AuthnRequest XML (se [```helpers.py```](https://github.com/Msurrow/websso-poc/blob/master/helpers.py))
I AuthnRequest XML sættes følgende værdier:

- ```IssueInstant``` attributten sættes i ```AuthnRequest``` elementet
- ```ID``` attributten sættes i ```AuthnRequest``` elementet
- ```AssertionConsumerServiceURL ``` attributten sættes i ```AuthnRequest``` elementet
- ```Issuer``` elementet sættes

Element | Beskrivelse | Sammenhæng til Metadata
------- | ----------- | --------------------
```IssueInstant ``` | UTC Timestamp i ISO format. Skal ved hvert request ellers afvises request ved IdP. |Ingen
```ID ``` | Unikt ID på requests. Skal ved hvert request ellers afvises request ved IdP |Ingen
```AssertionConsumerServiceURL``` | Endpoint some IdP skal redirect til ved successfuld login _for dette request_. |Skal være én af endpoints defineret i ```AssertionConsumerService``` i metadata (se ovenfor).
```Issuer``` | Navn på Service Provider. |Skal være det samme som ```entityID``` defineret i metadata (se ovenfor).

### Sammenhæng mellem komponenter (request-login-response flow)
Sekvens af kald i det samlede setup foregår sådan:

- Bruger (via browser) åbner webklient siden:
    - 	```=> GET på '/' til Web-frontend server.```
- Web-frontend server svarer med html+javascript for client-side app
    - ```=> HTTP 200, sender index.html + webclient.js```
- Bruger/Browser trykker på "Hent data"-knap i brugergrænseflade. Javascript webklient laver AJAX-request til Service Provider API endpoint for at få data.
    - ```=> GET http://websoo-poc.herokuapp.com/kai-themes```
- Service Provider tjekker om brugeren sender autentifikation i request. Brugeren har ikke endnu autentificeret sig, så derfor er autentifikation ikke del af request (ingen sikkerheds kontekst). Service Provider svarer med XHTML-form der indeholder SAML ```AuthnRequest```.
    - => Sender XHTML-form retur i data del af HTTP response. Under XML beskrives de tre tre relevante elementer, som XHTML-formen indeholder:
 ```xml
 <form method="post" action="{}">
	<input type="hidden" name="SAMLRequest" value="{}" />
	<input type="hidden" name="RelayState" value="" />
	<input type="submit" value="Login" />
</form>
```

Elemet | Attribut | Beskrivelse
------ | -------- | -----------
```form ``` | ```action``` | Indeholder IdP'ens URL, som POST request sendes til. I eksemplet anvendes: <https://idp.testshib.org/idp/profile/SAML2/POST/SSO>. Heri bestemmes hvordan der omstilles til den korrekt login side. Se detaljer for POST-binding i [SAML-bindings].
```input name="SAMLRequest" ``` | ```value``` | Indeholder den SAML AuthnRequest, som Service Provideren har genereret (se AuthnRequest XML ovenfor). Base-64 encoded. Se detaljer for AuthnRequest i [SAML-Core].
```input name="RelayState" ``` | ```value``` | ReplayState kan anvendes til at "gemme" state fra inden serveren satte SAML login forløb igang (dvs. omstilling til IdP). Heri gemmer vi det endpoint, som vores Web-frontend server har, der kan håndtere modtagelsen af token fra Service Provider. I eksemplet her sættes RelayState i webklienten (se [```webclient.js```](https://github.com/Msurrow/websso-poc/blob/master/webapp/static/webclient.js)). RelayState endpoint sættes til <http://localhost:8000/login_complete>, da Webfront-end Serveren kører på localhost, og login_complete er lavet til at håndtere modtagelsen af en token.

- Webklient modtager svar fra Service Provider, identificere at der kom et SAML AuthnRequest retur (evt via HTTP response kode) i form af XHTML-form. Webklient viser XHTML-form for brugeren. Brugern kan trykke på "Login"-knappen.
- XHTML-formens action-attribut indeholder url til IdP, hvorfor Webklienten ved tryk på "Login"-knap sender et POST request til IdP'en, med AuthnRequest som angivet i XHTML-formen (```input name="SAMLRequest" ```-attribut). RelayState (```input name="RelayState" ```-attribut) medsendes også - IdP'en anvender ikke denne til noget, men medsender den til Service Provider, efter login er gennemført. Bemærk vi sætter RelayState i webklienten, som beskrevet ovenfor. 
    - ```=> POST til https://idp.testshib.org/idp/profile/SAML2/POST/SSO?SAMLRequest=<AuthnRequest_b64_encoded>&RelayState=http://localhost:8000/login_complete```
- IdP laver login forløb med browser/brugeren. Efter successfuld login genererer IdP'en en ```SAML Response```, indeholdende ```SAML Assertion```, som beviser brugerens autenticitet. IdP'en sender en REDIRECT til Service Provideren på den url, der er angivet i hhv. metadata og ```AuthnRequest```.
    - ```=> Redirect 302 Location: http://websso-poc.herokuapp.com/saml_login_success``` med ```SAMLResponse``` og ```RelayState``` i request.
- Browser følger redirect
    - ```=> GET http://websso-poc.herokuapp.com/saml_login_success``` med ```SAMLResponse``` og ```RelayState``` URL encoded
- Service Provider modtager POST request fra IdP og behandler requestet. I eksemplet er det handler'en for endpoint ```/kai-themes```. Da GET request nu indeholder et gyldig ```SAML Response```, generere Service Provider en token. Service Provider læser også ```RelayState``` og token returneres til Webfront-end server, på det endpoint der er angivet i RelayState.
    - ```=> Redirect 302 Location: http://localhost:8000/login_complete?token=<genereret_token>```
- Browser følger redirect
    - ```=> GET http://localhost:8000/login_complete?token=<genereret_token>```
- Web-frontend Serveren modtager token via request og viser siden til brugeren, hvor denne er logget ind. Brugeren kan nu bruge "Hent data" knappen igen, til at hente data fra Service Provideren.

#### RelayState

I Poc'en er ```RelayState``` kun brugt til at afsluttet forløbet med at vise ```index.html``` med token hentet. ```RelayState``` kunne lige så vel bruges til at gemme Webklientens faktiske state, sådan at ```/login_complete``` endpointet kunne fortsætte med det oprindelige API kald, der satte SAML login processen igang. 

## Referencer <a name="referencer"></a>

\[SAML]: <https://wiki.oasis-open.org/security/FrontPage#SAML_V2.0_Standard>

\[SAML-core]: <http://www.oasis-open.org/committees/download.php/56776/sstc-saml-core-errata-2.0-wd-07.pdf>

\[SAML-profil]: <http://www.oasis-open.org/committees/download.php/56782/sstc-saml-profiles-errata-2.0-wd-07.pdf>

\[SAML-bindings]: <http://www.oasis-open.org/committees/download.php/56779/sstc-saml-bindings-errata-2.0-wd-06.pdf>

\[SAML-technical overview]: <https://www.oasis-open.org/committees/download.php/11511/sstc-saml-tech-overview-2.0-draft-03.pdf>

## 10 second guide til installation af Python og dependencies <a name="deps"></a>
For at afvikle PoC koden selv skal følgende dependencies installeres:

- Python 3 [Link](https://www.python.org/downloads/)
- Pip _(kommer som del af standard installation ved Python 3.4+)_
- (evt. VirtualEnvironment) [Link](https://virtualenv.pypa.io/en/stable/installation/)

Step-by-step installation (antaget ovenstående dependencies er installeret):

Check projekt ud fra GIT:

```
~#: git clone https://github.com/Msurrow/websso-poc.git
~#: cd websso-poc/
```

Lav virtual environment (optional):

```
~#: virtualenv venv_websso
~#: source venv_websso/bin/activate
```

Installer dependencies med PIP:

```
~#: pip install -r requirements.txt 
```

Done.

## Debugging
### IdP
Hvis IdP'en giver følgende fejl:

```
SAML 2 SSO Profile is not configured for ...
```

Tjek da at:

- SP metadata er uploaded til IdP via registreringssiden
- "valid until" attributten i metadata

### Installation af python / virtualenv / dependencies
Hvis du har problemer med at installere pkgconfig pakken, fordi en "nose>=1.3" dependency mangler, kan du installere nose-pakken manuelt og køre ovenstående kommando igen: 

```~#: pip install nose```

```~#: pip install -r requirements.txt```

Hvis "pip" ikke findes og du lige har installeret python3 fra ovenstående link, skal du bruge "pip3" istedet for (dvs. i alle ovenstående kommandoer).