conda activate arxiv-summary

python -m src.data.fetch_arxiv 

python -m src.data.download_pdfs

docker pull lfoppiano/grobid:0.7.3

docker run -d -p 8070:8070 lfoppiano/grobid:0.7.3

python -m src.data.parse_pdf

python -m src.data.parse_xml

python -m src.data.dataset

python -m src.models.train_t5 --target abstract

python -m src.models.train_t5 --target introduction

python -m src.models.train_t5 --target conclusion

python -m src.models.metrics



    target       eval_loss  rouge1  rouge2  rougeL  epoch
    abstract      0.176062  0.6942  0.6257  0.6386    1.0
    conclusion    4.170982  0.2641  0.0772  0.1797    1.0
    introduction  3.719965  0.1615  0.0236  0.1175    1.0