# epubToWeb
converte um arquivo epub para um 'site'

![an example](https://user-images.githubusercontent.com/30227872/113874322-0fba1100-978c-11eb-87e8-16a2a0e3f6b5.png)

./main.py ARQUIVO.epub PASTA_DO_WEB_BOOK
book.html: o arquivo que tu vai abrir no broswer. tem um iframe com teu livro

bookIndex.html: indice dos arquivos (lista de links). o arquivo que vai ta no iframe

bookContent/ : os arquivos do epub

extractedEpub/ : pasta aonde o conteudo do arquivo foi extraido

[eng]
converts an epub file to a 'website'

$ ./main.py FILE.epub WEB_BOOK_FOLDER
book.html: the file you'll open in your browser. it contains an iframe with the book on it

bookIndex.html: a list with links to the epub content

bookContent/ : the folder which contains the epub files

extractedEpub/ : the folder where the epub was extracted. it can be deleted
