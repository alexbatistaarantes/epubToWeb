# epubToWeb

extrai o teu epub, chama o programa (./main.py PASTA_COM_OS_HTML NOVA_PASTA_COM_O_LIVRO) e ai vai modificar pra ficar melhor pra ler no browser
book.html: o arquivo que tu vai abrir no broswer. tem um iframe com teu livro
bookIndex.html: indice dos arquivos (lista de links). o arquivo que vai ta no iframe
pages/: os arquivos html que estavam na pasta informada. eles sao modificados pra incluir links pros arquivos anterior e próximo e pro bookIndex.html
