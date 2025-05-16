import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, FeedbackLabel, Purchase, Feedback, Label
from app.ai_processing import FeedbackAnalyzer

# Configuração do banco de dados
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/feedback_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar tabelas se não existirem
Base.metadata.create_all(bind=engine)

# Inicializar o analisador de feedback
analyzer = FeedbackAnalyzer()

def create_sample_data(db):
    # Rótulos pré-definidos
    predefined_labels = [
        "qualidade", "durabilidade", "desempenho", "funcionalidade", "design",
        "ergonomia", "material", "tamanho", "cor", "acessórios",
        "entrega", "prazo_entrega", "frete", "rastreamento", "embalagem",
        "instalação", "garantia", "suporte", "preço", "valor",
        "promoção", "desconto", "pagamento", "parcelamento", "atendimento",
        "resposta", "solucao", "reclamacao", "elogio", "sugestao"
    ]
    
    # Criar rótulos no banco de dados
    for label_name in predefined_labels:
        if not db.query(Label).filter(Label.name == label_name).first():
            db_label = Label(name=label_name, description=f"Rótulo para {label_name}")
            db.add(db_label)
    db.commit()

    # Produtos de exemplo
    products = [
        # Eletrônicos
        {"id": "P100", "name": "Smartphone X Pro", "price_range": (2500, 4000)},
        {"id": "P101", "name": "Notebook Ultra Slim", "price_range": (3500, 8500)},
        {"id": "P102", "name": "Fone Bluetooth Elite", "price_range": (200, 600)},
        {"id": "P103", "name": "Smart TV 55\" 4K", "price_range": (2500, 5500)},
        {"id": "P104", "name": "Tablet Pro 10.5\"", "price_range": (1200, 2800)},
        {"id": "P105", "name": "Smartwatch Fitness", "price_range": (400, 1200)},
        {"id": "P106", "name": "Câmera DSLR Profissional", "price_range": (3000, 8000)},
        {"id": "P107", "name": "Console de Games Elite", "price_range": (2500, 5000)},
        {"id": "P108", "name": "Caixa de Som Bluetooth", "price_range": (150, 800)},
        {"id": "P109", "name": "Drone 4K com Câmera", "price_range": (800, 3000)},

        # Informática
        {"id": "P110", "name": "Monitor Gamer 27\"", "price_range": (1200, 3000)},
        {"id": "P111", "name": "Teclado Mecânico RGB", "price_range": (200, 800)},
        {"id": "P112", "name": "Mouse Sem Fio", "price_range": (50, 300)},
        {"id": "P113", "name": "HD Externo 1TB", "price_range": (200, 600)},
        {"id": "P114", "name": "SSD 500GB", "price_range": (300, 700)},
        {"id": "P115", "name": "Webcam Full HD", "price_range": (150, 500)},
        {"id": "P116", "name": "Impressora Multifuncional", "price_range": (500, 1500)},
        {"id": "P117", "name": "Roteador Wi-Fi 6", "price_range": (300, 900)},
        {"id": "P118", "name": "Mesa Digitalizadora Pro", "price_range": (400, 1500)},
        {"id": "P119", "name": "Carregador Portátil 20000mAh", "price_range": (100, 400)},

        # Eletrodomésticos
        {"id": "P120", "name": "Geladeira Frost Free", "price_range": (2000, 6000)},
        {"id": "P121", "name": "Fogão 5 Bocas", "price_range": (800, 2500)},
        {"id": "P122", "name": "Máquina de Lavar 12kg", "price_range": (1500, 4000)},
        {"id": "P123", "name": "Micro-ondas 30L", "price_range": (400, 1200)},
        {"id": "P124", "name": "Ar Condicionado Split", "price_range": (1500, 5000)},
        {"id": "P125", "name": "Aspirador Robô", "price_range": (800, 3000)},
        {"id": "P126", "name": "Liquidificador Potente", "price_range": (100, 400)},
        {"id": "P127", "name": "Batedeira Planetária", "price_range": (200, 800)},
        {"id": "P128", "name": "Ferro de Passar a Vapor", "price_range": (100, 500)},
        {"id": "P129", "name": "Ventilador Turbo", "price_range": (80, 300)},

        # Móveis
        {"id": "P130", "name": "Sofá 3 Lugares", "price_range": (1200, 5000)},
        {"id": "P131", "name": "Mesa de Jantar 6 Lugares", "price_range": (800, 3500)},
        {"id": "P132", "name": "Cama Queen Size", "price_range": (1000, 4000)},
        {"id": "P133", "name": "Guarda-Roupa Casal", "price_range": (1500, 6000)},
        {"id": "P134", "name": "Escritório Completo", "price_range": (2000, 8000)},
        {"id": "P135", "name": "Poltrona Reclinável", "price_range": (500, 2500)},
        {"id": "P136", "name": "Estante para Livros", "price_range": (200, 1200)},
        {"id": "P137", "name": "Rack para TV", "price_range": (300, 1500)},
        {"id": "P138", "name": "Cômoda 5 Gavetas", "price_range": (400, 2000)},
        {"id": "P139", "name": "Banqueta Alta", "price_range": (100, 500)},

        # Moda
        {"id": "P140", "name": "Tênis Esportivo", "price_range": (150, 600)},
        {"id": "P141", "name": "Camisa Social", "price_range": (80, 300)},
        {"id": "P142", "name": "Vestido Elegante", "price_range": (120, 500)},
        {"id": "P143", "name": "Calça Jeans", "price_range": (100, 400)},
        {"id": "P144", "name": "Jaqueta de Couro", "price_range": (300, 1200)},
        {"id": "P145", "name": "Bolsa Feminina", "price_range": (80, 800)},
        {"id": "P146", "name": "Relógio de Pulso", "price_range": (200, 2000)},
        {"id": "P147", "name": "Óculos de Sol", "price_range": (100, 1000)},
        {"id": "P148", "name": "Cinto de Couro", "price_range": (50, 300)},
        {"id": "P149", "name": "Chapéu Estiloso", "price_range": (60, 400)},

        # Esportes
        {"id": "P150", "name": "Bicicleta Esportiva", "price_range": (800, 5000)},
        {"id": "P151", "name": "Esteira Elétrica", "price_range": (1500, 6000)},
        {"id": "P152", "name": "Halteres Ajustáveis", "price_range": (100, 800)},
        {"id": "P153", "name": "Bola de Futebol", "price_range": (50, 300)},
        {"id": "P154", "name": "Raquete de Tênis", "price_range": (200, 1200)},
        {"id": "P155", "name": "Skate Profissional", "price_range": (300, 1500)},
        {"id": "P156", "name": "Luva de Boxe", "price_range": (80, 500)},
        {"id": "P157", "name": "Corda para Pular", "price_range": (20, 150)},
        {"id": "P158", "name": "Tênis de Corrida", "price_range": (200, 800)},
        {"id": "P159", "name": "Mochila para Trekking", "price_range": (150, 700)},

        # Beleza
        {"id": "P160", "name": "Kit Maquiagem Profissional", "price_range": (150, 1000)},
        {"id": "P161", "name": "Secador de Cabelo", "price_range": (80, 500)},
        {"id": "P162", "name": "Chapinha Cerâmica", "price_range": (100, 600)},
        {"id": "P163", "name": "Creme Facial", "price_range": (40, 300)},
        {"id": "P164", "name": "Perfume Importado", "price_range": (120, 800)},
        {"id": "P165", "name": "Aparelho de Barbear", "price_range": (50, 400)},
        {"id": "P166", "name": "Esmalte Longa Duração", "price_range": (10, 50)},
        {"id": "P167", "name": "Batom Líquido", "price_range": (20, 100)},
        {"id": "P168", "name": "Máscara para Cílios", "price_range": (30, 150)},
        {"id": "P169", "name": "Kit Cuidados com a Barba", "price_range": (60, 300)},

        # Livros
        {"id": "P170", "name": "Livro Best-seller", "price_range": (30, 120)},
        {"id": "P171", "name": "Coleção Completa", "price_range": (200, 800)},
        {"id": "P172", "name": "Livro Infantil", "price_range": (20, 80)},
        {"id": "P173", "name": "Enciclopédia", "price_range": (150, 600)},
        {"id": "P174", "name": "Livro Técnico", "price_range": (50, 300)},
        {"id": "P175", "name": "Revista Especializada", "price_range": (10, 50)},
        {"id": "P176", "name": "Audiobook", "price_range": (40, 150)},
        {"id": "P177", "name": "Livro de Receitas", "price_range": (40, 120)},
        {"id": "P178", "name": "Livro de Colorir", "price_range": (25, 80)},
        {"id": "P179", "name": "Dicionário", "price_range": (50, 150)},

        # Bebês
        {"id": "P180", "name": "Carrinho de Bebê", "price_range": (400, 2000)},
        {"id": "P181", "name": "Moisés", "price_range": (200, 800)},
        {"id": "P182", "name": "Kit Berço", "price_range": (300, 1500)},
        {"id": "P183", "name": "Mamadeira", "price_range": (20, 100)},
        {"id": "P184", "name": "Fraldas", "price_range": (40, 200)},
        {"id": "P185", "name": "Chupeta", "price_range": (10, 50)},
        {"id": "P186", "name": "Brinquedo Educativo", "price_range": (30, 150)},
        {"id": "P187", "name": "Kit Banho", "price_range": (50, 200)},
        {"id": "P188", "name": "Cadeirinha para Carro", "price_range": (300, 1200)},
        {"id": "P189", "name": "Babá Eletrônica", "price_range": (150, 600)}
    ]

    # Comentários de exemplo (positivos, neutros e negativos)
    sample_comments = [
        # Positivos
        
        # Satisfação geral com o produto
        "Adorei o produto! Superou minhas expectativas.",
        "Excelente qualidade, vale cada centavo.",
        "Entrega rápida e produto perfeito.",
        "Recomendo a todos, muito satisfeito!",
        "Funciona perfeitamente, atendimento impecável.",
        
        # Qualidade e desempenho
        "Produto de altíssima qualidade, nota 10!",
        "Super resistente e durável, exatamente o que precisava.",
        "Desempenho acima do esperado para o preço pago.",
        "Material premium, acabamento perfeito.",
        "Funcionalidade excelente, atende todas as necessidades.",
        
        # Entrega e embalagem
        "Chegou antes do prazo, muito bem embalado.",
        "Embalagem super reforçada, produto intacto.",
        "Logística impecável, rastreamento preciso.",
        "Entrega relâmpago, impressionante!",
        "Produto chegou em perfeito estado, embalagem luxuosa.",
        
        # Atendimento
        "Atendimento excepcional, tirou todas minhas dúvidas.",
        "Equipe super prestativa e educada.",
        "Problema resolvido em menos de 24h, incrível!",
        "Vendedor muito atencioso, superou expectativas.",
        "Pós-venda nota 1000, me senti muito bem atendido.",
        
        # Custo-benefício
        "Melhor custo-benefício que já vi no mercado.",
        "Qualidade que justifica plenamente o investimento.",
        "Preço justo para um produto desta qualidade.",
        "Promoção imperdível, produto de primeira linha.",
        "Vale cada centavo, durabilidade impressionante.",
        
        # Experiência de uso
        "Usabilidade intuitiva, fácil de configurar.",
        "Design moderno e ergonômico, muito confortável.",
        "Leve e prático, perfeito para uso diário.",
        "Super silencioso, qualidade impressionante.",
        "Consumo energético baixíssimo, economia garantida.",
        
        # Comparações
        "Muito melhor que modelos mais caros que já usei.",
        "Superou produtos de marcas renomadas.",
        "Diferença de qualidade é nítida em relação à concorrência.",
        "Único no mercado com estas características por este preço.",
        "Não encontrei similar com esta qualidade em lugar nenhum.",
        
        # Presentes e indicações
        "Presente perfeito, a pessoa amou!",
        "Todos estão me perguntando onde comprei.",
        "Já indiquei para vários amigos, produto fantástico.",
        "Com certeza comprarei outros itens da marca.",
        "Virei cliente fiel, qualidade consistente.",
        
        # Detalhes específicos
        "Bateria dura dias, exatamente como anunciado.",
        "Tela super nítida, cores vibrantes.",
        "Som de alta qualidade, grave potente.",
        "Conectividade excelente, sem falhas.",
        "Acessórios inclusos de ótima qualidade.",
        
        # Surpresas positivas
        "Veio com brinde exclusivo, surpresa maravilhosa!",
        "Superou em muito a descrição do site.",
        "Detalhes que não esperava, atenção aos mínimos aspectos.",
        "Material ainda melhor que nas fotos.",
        "Manual completo em português, raro encontrar.",

        # Garantia e confiança
        "Marca confiável, garantia extensa.",
        "Compra segura, sem arrependimentos.",
        "Política de trocas clara e transparente.",
        "Assistência técnica disponível e acessível.",
        "Produto testado e aprovado por especialistas.",
        
        # Neutros
        
        # Satisfação mediana
        "O produto é bom, mas a entrega atrasou um pouco.",
        "Cumpriu o básico, nada excepcional.",
        "Esperava um pouco mais pelo preço pago.",
        "Não tenho do que reclamar, mas também não me surpreendeu.",
        "Produto ok, mas a embalagem poderia ser melhor.",
        
        # Funcionalidade
        "Funciona, mas o design poderia ser mais moderno.",
        "Atende às necessidades básicas.",
        "Performance mediana para o preço.",
        "Faz o que promete, sem mais nem menos.",
        "Nada de especial, mas cumpre sua função.",
        
        # Entrega e logística
        "Entrega no prazo, produto conforme descrito.",
        "Chegou dentro do esperado, sem atrasos.",
        "Processo de compra normal, sem surpresas.",
        "Embalagem adequada, mas nada impressionante.",
        "Frete um pouco caro para o serviço oferecido.",
        
        # Atendimento
        "Atendimento normal, sem problemas.",
        "Sac respondeu dentro do prazo esperado.",
        "Atendimento padrão, nem bom nem ruim.",
        "Resolveram meu problema, mas demoraram mais que o necessário.",
        "Comunicação eficiente, mas pouco calorosa.",
        
        # Qualidade
        "Qualidade aceitável para o valor pago.",
        "Material razoável, não é premium mas também não é ruim.",
        "Acabamento poderia ser melhor, mas está dentro do normal.",
        "Durabilidade mediana, espero que dure um tempo razoável.",
        "Nada a reclamar da qualidade, mas também nada a destacar.",
        
        # Experiência geral
        "Nada a reclamar, mas também nada a elogiar.",
        "Satisfatório, mas não compraria novamente.",
        "Produto comum, igual a muitos outros no mercado.",
        "Não me arrependi, mas também não ficaria entusiasmado em recomendar.",
        "Experiência mediana, como a maioria das compras online.",
        
        # Comparações
        "Equivalente aos produtos similares do mercado.",
        "Não é melhor nem pior que a concorrência.",
        "Parecido com o que já usei antes, sem diferenças marcantes.",
        "Esperava algo diferente, mas é bem parecido com outros da categoria.",
        "Não destoa nem positiva nem negativamente em relação a outros.",
        
        # Características específicas
        "Tamanho adequado, nem grande nem pequeno demais.",
        "Peso dentro do esperado para este tipo de produto.",
        "Cor corresponde à mostrada no site, sem surpresas.",
        "Cheiro neutro, como esperado para o material.",
        "Textura comum, igual a outros produtos similares.",
        
        # Usabilidade
        "Instruções claras o suficiente para montar/usar.",
        "Curva de aprendizado normal para este tipo de produto.",
        "Interface intuitiva, mas poderia ser mais amigável.",
        "Fácil de usar, mas não especialmente prazeroso.",
        "Nada complicado, mas também nada inovador na usabilidade.",
        
        # Custo-benefício
        "Preço justo para o que oferece.",
        "Nem caro nem barato para a categoria.",
        "Promoção regular, nada extraordinário.",
        "Parcelamento sem juros, como é comum encontrar.",
        "Valor compatível com a experiência proporcionada.",
        
        # Recomendação
        "Talvez recomende, dependendo para quem.",
        "Compraria novamente se precisasse, mas não por preferência.",
        "Não desencorajo ninguém de comprar, mas também não incentivo.",
        "Solução aceitável para a necessidade.",
        "Opção válida entre outras equivalentes no mercado.",
        
        # Negativos
        
        # Qualidade do produto
        "Produto veio com defeito, muito decepcionado.",
        "Péssima qualidade, não vale o preço.",
        "Material frágil, quebrou com pouco uso.",
        "Acabamento porco, cheio de imperfeições.",
        "Produto de baixíssima qualidade, parece falsificado.",
        
        # Problemas com a entrega
        "Entrega atrasou mais de uma semana.",
        "Produto extraviado, tive que esperar semanas.",
        "Entregaram no endereço errado duas vezes.",
        "Embalagem veio totalmente amassada e danificada.",
        "Faltavam peças importantes na entrega.",
        
        # Erros no pedido
        "Comprei na promoção mas veio errado.",
        "Recebi um item completamente diferente.",
        "Cor errada, tamanho errado, tudo errado!",
        "Versão inferior à que eu havia comprado.",
        "Kit incompleto, faltavam acessórios essenciais.",
        
        # Atendimento ao cliente
        "Atendimento horrível, não resolveram meu problema.",
        "SAC inexistente, ninguém responde.",
        "Me enrolaram por semanas sem solução.",
        "Atendente mal educado e despreparado.",
        "Política de trocas complicada de propósito.",
        
        # Descrição do produto
        "Produto completamente diferente da descrição.",
        "Anúncio enganoso, características inventadas.",
        "Fotos do site não correspondem à realidade.",
        "Funcionalidades que prometeram não existem.",
        "Muito menor do que aparecia nas imagens.",
        
        # Durabilidade
        "Quebrou após uma semana de uso.",
        "Parou de funcionar depois de 3 dias.",
        "Desbotou na primeira lavagem.",
        "Costuras arrebentando com pouco uso.",
        "Descascou completamente em um mês.",
        
        # Tamanho e adequação
        "Muito pequeno, não atendeu minhas expectativas.",
        "Tamanho completamente fora do padrão.",
        "Não serve no propósito anunciado.",
        "Ergonômico? Mais como desconfortável!",
        "Peso muito acima do especificado.",
        
        # Garantia e suporte
        "Não recomendo, problema com garantia.",
        "Assistência técnica não honra a garantia.",
        "Custaram a enviar peça de reposição.",
        "Quase um mês para consertar defeito de fábrica.",
        "Tive que acionar o PROCON para resolver.",
        
        # Experiência geral
        "Pior experiência de compra que já tive.",
        "Perda de tempo e dinheiro, lamento ter comprado.",
        "Nunca mais compro nesta loja!",
        "Arrependimento total da compra.",
        "Nota zero, produto horrível!",
        
        # Segurança e saúde
        "Produto perigoso, quase causou acidente.",
        "Cheiro forte de químico que não sai.",
        "Alergia terrível ao material utilizado.",
        "Partes soltas que podem engasgar crianças.",
        "Superfície cortante mal acabada.",
        
        # Funcionalidade
        "Não funciona como deveria.",
        "Toda hora dá problema, muito instável.",
        "Interface confusa e cheia de bugs.",
        "Consome energia demais para pouco resultado.",
        "Barulho insuportável quando ligado.",
        
        # Custo-benefício
        "Caríssimo para a qualidade oferecida.",
        "Promoção enganosa, preço inflado.",
        "Não vale nem metade do que cobram.",
        "Gastar mais com consertos que com o produto.",
        "Investimento perdido, dinheiro jogado fora.",
        
        # Ética e confiança
        "Claro caso de propaganda enganosa.",
        "Marca desonesta, não cumpre o prometido.",
        "Produto reembalado vendido como novo.",
        "Nota fiscal com valores divergentes.",
        "Prática comercial abusiva, vou denunciar."
    ]

    # Gerar 30 compras com feedbacks
    for i in range(1, 201):
        # Selecionar um produto aleatório
        product = random.choice(products)
        price = random.randint(*product["price_range"])
        
        # Criar compra
        purchase = Purchase(
            customer_id=f"CUST{1000 + i}",
            product_id=product["id"],
            product_name=product["name"],
            amount=price,
            purchase_date=datetime.now() - timedelta(days=random.randint(1, 60))
        )
        db.add(purchase)
        db.commit()
        
        # Selecionar um comentário aleatório
        comment = random.choice(sample_comments)
        
        # Analisar sentimento
        sentiment = analyzer.analyze_sentiment(comment)
        
        # Map sentiment to label
        if sentiment["label"] in ["positive", "pos"]:
            sentiment["label"] = "Positivo"
        elif sentiment["label"] in ["negative", "neg"]:
            sentiment["label"] = "Negativo"
        else:
            sentiment["label"] = "Neutro"
                
        # Criar feedback
        feedback = Feedback(
            purchase_id=purchase.id,
            comment=comment,
            sentiment_score=sentiment["score"],
            sentiment_label=sentiment["label"]
        )
        db.add(feedback)
        db.commit()
        
        # Gerar rótulos automaticamente
        existing_labels = [label.name for label in db.query(Label).all()]
        labels = analyzer.generate_labels(comment, existing_labels)
        
        # Associar rótulos ao feedback
        for label_name in labels:
            label = db.query(Label).filter(Label.name == label_name).first()
            if label:
                feedback_label = FeedbackLabel(
                    feedback_id=feedback.id,
                    label_id=label.id
                )
                db.add(feedback_label)
        
        db.commit()
        
        print(f"Adicionado: Compra {i} com feedback - {comment[:30]}...")

    analyzer.shutdown()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_sample_data(db)
        print("Banco de dados populado com sucesso!")
    except Exception as e:
        print(f"Erro ao popular banco de dados: {e}")
    finally:
        db.close()