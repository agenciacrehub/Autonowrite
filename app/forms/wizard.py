from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, IntegerField, validators
from wtforms.validators import DataRequired, Length, Optional, NumberRange, InputRequired
from flask_wtf.file import FileField, FileAllowed

class RequiredIf(validators.DataRequired):
    """Validator which makes a field required if another field is set and has a truthy value."""
    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super().__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception(f'No field named "{self.other_field_name}" in form')
        if bool(other_field.data):
            super().__call__(form, field)

class WizardStep1Form(FlaskForm):
    """Step 1: Context and Domain"""
    project_title = StringField('Título do Projeto', 
                              validators=[
                                  DataRequired(message='O título do projeto é obrigatório'),
                                  Length(min=5, max=100, message='O título deve ter entre 5 e 100 caracteres')
                              ],
                              render_kw={
                                  'minlength': 5,
                                  'maxlength': 100,
                                  'data-msg-required': 'Por favor, insira um título para o projeto',
                                  'data-msg-minlength': 'O título deve ter pelo menos 5 caracteres',
                                  'data-msg-maxlength': 'O título não pode ter mais de 100 caracteres'
                              })
                              
    knowledge_domain = StringField('Domínio de Conhecimento',
                                 validators=[
                                     DataRequired(message='O domínio de conhecimento é obrigatório'),
                                     Length(min=3, max=100, message='O domínio deve ter entre 3 e 100 caracteres')
                                 ],
                                 render_kw={
                                     'minlength': 3,
                                     'maxlength': 100,
                                     'data-msg-required': 'Por favor, informe o domínio de conhecimento',
                                     'data-msg-minlength': 'O domínio deve ter pelo menos 3 caracteres'
                                 })
                                  
    target_audience = StringField('Público-Alvo',
                                validators=[
                                    DataRequired(message='O público-alvo é obrigatório'),
                                    Length(min=3, max=100, message='O público-alvo deve ter entre 3 e 100 caracteres')
                                ],
                                render_kw={
                                    'minlength': 3,
                                    'maxlength': 100,
                                    'data-msg-required': 'Por favor, informe o público-alvo',
                                    'data-msg-minlength': 'O público-alvo deve ter pelo menos 3 caracteres'
                                })
                                
    technical_level = SelectField('Nível Técnico',
                                choices=[
                                    ('', 'Selecione um nível...'),
                                    ('iniciante', 'Iniciante'),
                                    ('intermediario', 'Intermediário'),
                                    ('avancado', 'Avançado'),
                                    ('academico', 'Acadêmico')
                                ],
                                validators=[
                                    InputRequired(message='Por favor, selecione um nível técnico')
                                ])
                                
    background_info = TextAreaField('Contexto Adicional',
                                  validators=[
                                      Optional(),
                                      Length(max=1000, message='O contexto adicional não pode ter mais de 1000 caracteres')
                                  ],
                                  render_kw={
                                      'maxlength': 1000,
                                      'data-msg-maxlength': 'O contexto adicional não pode ter mais de 1000 caracteres',
                                      'rows': 3
                                  })
                                  
    next = SubmitField('Próximo', render_kw={'class': 'btn btn-primary'})
    
    def validate(self, **kwargs):
        # Standard validation
        if not super().validate():
            return False
            
        # Additional custom validation can be added here
        return True

class WizardStep2Form(FlaskForm):
    """Step 2: Objectives"""
    main_purpose = TextAreaField('Propósito Principal',
                               validators=[
                                   DataRequired(message='O propósito principal é obrigatório'),
                                   Length(min=10, max=500, message='O propósito principal deve ter entre 10 e 500 caracteres')
                               ],
                               render_kw={
                                   'minlength': 10,
                                   'maxlength': 500,
                                   'rows': 4,
                                   'data-msg-required': 'Por favor, descreva o propósito principal',
                                   'data-msg-minlength': 'O propósito principal deve ter pelo menos 10 caracteres'
                               })
                               
    learning_objectives = TextAreaField('Objetivos de Aprendizado',
                                      validators=[
                                          Optional(),
                                          Length(max=1000, message='Os objetivos de aprendizado não podem ter mais de 1000 caracteres')
                                      ],
                                      render_kw={
                                          'maxlength': 1000,
                                          'rows': 3,
                                          'placeholder': 'O que os leitores devem aprender com este conteúdo?'
                                      })
                                      
    call_to_action = StringField('Chamada para Ação',
                               validators=[
                                   Optional(),
                                   Length(max=200, message='A chamada para ação não pode ter mais de 200 caracteres')
                               ],
                               render_kw={
                                   'maxlength': 200,
                                   'placeholder': 'O que você quer que o leitor faça após a leitura?'
                               })
                               
    next = SubmitField('Próximo', render_kw={'class': 'btn btn-primary'})
    back = SubmitField('Voltar', render_kw={'class': 'btn btn-secondary'})
    
    def validate(self, **kwargs):
        if not super().validate():
            return False
        return True

class WizardStep3Form(FlaskForm):
    """Step 3: Scope and Limitations"""
    must_include = TextAreaField('Deve Incluir',
                               validators=[
                                   Optional(),
                                   Length(max=1000, message='O campo não pode ter mais de 1000 caracteres')
                               ],
                               render_kw={
                                   'maxlength': 1000,
                                   'rows': 3,
                                   'placeholder': 'Quais tópicos ou informações devem ser incluídos?'
                               })
                               
    must_exclude = TextAreaField('Deve Excluir',
                               validators=[
                                   Optional(),
                                   Length(max=1000, message='O campo não pode ter mais de 1000 caracteres')
                               ],
                               render_kw={
                                   'maxlength': 1000,
                                   'rows': 3,
                                   'placeholder': 'Há algum tópico que deve ser evitado?'
                               })
                               
    word_count = IntegerField('Número de Palavras Alvo',
                            validators=[
                                Optional(),
                                NumberRange(min=100, max=10000, message='O número de palavras deve estar entre 100 e 10000')
                            ],
                            render_kw={
                                'min': 100,
                                'max': 10000,
                                'placeholder': 'Opcional, padrão: 1000',
                                'data-msg-number': 'Por favor, insira um número válido',
                                'data-msg-min': 'Mínimo de 100 palavras',
                                'data-msg-max': 'Máximo de 10000 palavras'
                            })
                            
    depth_level = SelectField('Nível de Profundidade', 
                            choices=[
                                ('1', 'Básico (Visão Geral)'),
                                ('2', 'Intermediário (Detalhado)'),
                                ('3', 'Avançado (Técnico)'),
                                ('4', 'Especializado (Acadêmico)'),
                                ('5', 'Especializado (Pesquisa)')
                            ],
                            default='2')
    next = SubmitField('Próximo', render_kw={'class': 'btn btn-primary'})
    back = SubmitField('Voltar', render_kw={'class': 'btn btn-secondary'})
    
    def validate(self, **kwargs):
        if not super().validate():
            return False
        return True

class WizardStep4Form(FlaskForm):
    """Step 4: Sources and References"""
    preferred_sources = TextAreaField('Fontes Preferenciais',
                                   validators=[
                                       Optional(),
                                       Length(max=1000, message='As fontes não podem ter mais de 1000 caracteres')
                                   ],
                                   render_kw={
                                       'maxlength': 1000,
                                       'rows': 3,
                                       'placeholder': 'Links ou nomes de fontes confiáveis que devem ser usadas'
                                   })
                                   
    key_authors = StringField('Autores de Referência',
                             validators=[
                                 Optional(),
                                 Length(max=200, message='Os nomes dos autores não podem ter mais de 200 caracteres')
                             ],
                             render_kw={
                                 'maxlength': 200,
                                 'placeholder': 'Autores importantes no assunto'
                             })
                             
    time_period = StringField('Período Temporal',
                             validators=[
                                 Optional(),
                                 Length(max=100, message='O período temporal não pode ter mais de 100 caracteres')
                             ],
                             render_kw={
                                 'maxlength': 100,
                                 'placeholder': 'Ex: Século XX, 2000-2010, etc.'
                             })
                             
    citations_required = BooleanField('Citações Obrigatórias',
                                    default=True,
                                    render_kw={
                                        'data-toggle': 'toggle',
                                        'data-on': 'Sim',
                                        'data-off': 'Não',
                                        'data-onstyle': 'success',
                                        'data-offstyle': 'secondary'
                                    })
                                    
    min_sources = IntegerField('Número Mínimo de Fontes',
                             validators=[
                                 Optional(),
                                 NumberRange(min=1, max=20, message='O número de fontes deve estar entre 1 e 20')
                             ],
                             default=3,
                             render_kw={
                                 'min': 1,
                                 'max': 20,
                                 'data-msg-number': 'Por favor, insira um número válido',
                                 'data-msg-min': 'Mínimo de 1 fonte',
                                 'data-msg-max': 'Máximo de 20 fontes'
                             })
                             
    next = SubmitField('Próximo', render_kw={'class': 'btn btn-primary'})
    back = SubmitField('Voltar', render_kw={'class': 'btn btn-secondary'})
    
    def validate(self, **kwargs):
        if not super().validate():
            return False
        return True

class WizardStep5Form(FlaskForm):
    """Step 5: Style and Formatting"""
    writing_tone = SelectField('Tom de Escrita',
                             choices=[
                                 ('', 'Selecione um tom...'),
                                 ('formal', 'Formal'),
                                 ('academico', 'Acadêmico'),
                                 ('conversacional', 'Conversacional'),
                                 ('persuasivo', 'Persuasivo'),
                                 ('informativo', 'Informativo')
                             ],
                             default='academico',
                             validators=[
                                 InputRequired(message='Por favor, selecione um tom de escrita')
                             ],
                             render_kw={
                                 'data-msg-required': 'Por favor, selecione um tom de escrita'
                             })
                             
    language = SelectField('Idioma',
                         choices=[
                             ('pt-BR', 'Português (Brasil)'),
                             ('pt-PT', 'Português (Portugal)'),
                             ('en-US', 'English (US)')
                         ],
                         validators=[
                             InputRequired(message='Por favor, selecione um idioma')
                         ],
                         render_kw={
                             'data-msg-required': 'Por favor, selecione um idioma'
                         })
                         
    required_sections = TextAreaField('Seções Obrigatórias',
                                    validators=[
                                        Optional(),
                                        Length(max=500, message='As seções não podem ter mais de 500 caracteres')
                                    ],
                                    render_kw={
                                        'maxlength': 500,
                                        'rows': 3,
                                        'placeholder': 'Ex: Introdução, Metodologia, Conclusão (uma por linha)'
                                    })
                                    
    formatting_guidelines = TextAreaField('Diretrizes de Formatação',
                                        validators=[
                                            Optional(),
                                            Length(max=1000, message='As diretrizes não podem ter mais de 1000 caracteres')
                                        ],
                                        render_kw={
                                            'maxlength': 1000,
                                            'rows': 3,
                                            'placeholder': 'Alguma orientação específica de formatação?'
                                        })
                                        
    next = SubmitField('Revisar', render_kw={'class': 'btn btn-primary'})
    back = SubmitField('Voltar', render_kw={'class': 'btn btn-secondary'})
    
    def validate(self, **kwargs):
        if not super().validate():
            return False
        return True

class WizardReviewForm(FlaskForm):
    """Final Review Step"""
    submit = SubmitField('Criar Projeto')
    back = SubmitField('Voltar')
    save_draft = SubmitField('Salvar Rascunho')

class CombinedWizardForm(FlaskForm):
    """Combined form with all wizard steps"""
    # Step 1 fields
    project_title = StringField('Título do Projeto', 
                              validators=[
                                  DataRequired(message='O título do projeto é obrigatório'),
                                  Length(min=5, max=100, message='O título deve ter entre 5 e 100 caracteres')
                              ])
                              
    knowledge_domain = StringField('Domínio de Conhecimento',
                                 validators=[
                                     DataRequired(message='O domínio de conhecimento é obrigatório'),
                                     Length(min=3, max=100, message='O domínio deve ter entre 3 e 100 caracteres')
                                 ])
                                  
    target_audience = StringField('Público-Alvo',
                                validators=[
                                    DataRequired(message='O público-alvo é obrigatório'),
                                    Length(min=3, max=100, message='O público-alvo deve ter entre 3 e 100 caracteres')
                                ])
                                
    technical_level = SelectField('Nível Técnico',
                                choices=[
                                    ('', 'Selecione um nível...'),
                                    ('iniciante', 'Iniciante'),
                                    ('intermediario', 'Intermediário'),
                                    ('avancado', 'Avançado'),
                                    ('academico', 'Acadêmico')
                                ],
                                validators=[
                                    InputRequired(message='Por favor, selecione um nível técnico')
                                ])
                                
    background_info = TextAreaField('Contexto Adicional',
                                  validators=[Optional(), Length(max=1000)])

    # Step 2 fields
    main_purpose = TextAreaField('Propósito Principal',
                               validators=[
                                   DataRequired(message='O propósito principal é obrigatório'),
                                   Length(min=10, max=500, message='O propósito principal deve ter entre 10 e 500 caracteres')
                               ])
                               
    learning_objectives = TextAreaField('Objetivos de Aprendizado',
                                      validators=[Optional(), Length(max=1000)])
                                      
    success_criteria = TextAreaField('Critérios de Sucesso',
                                   validators=[Optional(), Length(max=500)])

    # Step 3 fields
    content_type = SelectField('Tipo de Conteúdo',
                             choices=[
                                 ('', 'Selecione o tipo...'),
                                 ('artigo', 'Artigo'),
                                 ('tutorial', 'Tutorial'),
                                 ('guia', 'Guia'),
                                 ('relatorio', 'Relatório'),
                                 ('apresentacao', 'Apresentação')
                             ],
                             validators=[InputRequired(message='Por favor, selecione o tipo de conteúdo')])
    
    structure_preference = SelectField('Estrutura Preferida',
                                     choices=[
                                         ('', 'Selecione a estrutura...'),
                                         ('linear', 'Linear (sequencial)'),
                                         ('modular', 'Modular (seções independentes)'),
                                         ('hierarquica', 'Hierárquica (tópicos e subtópicos)'),
                                         ('comparativa', 'Comparativa (análise de alternativas)')
                                     ],
                                     validators=[InputRequired(message='Por favor, selecione a estrutura')])
    
    sections_topics = TextAreaField('Seções e Tópicos',
                                  validators=[Optional(), Length(max=1000)])

    # Step 4 fields
    writing_style = SelectField('Estilo de Escrita',
                              choices=[
                                  ('', 'Selecione o estilo...'),
                                  ('academico', 'Acadêmico'),
                                  ('jornalistico', 'Jornalístico'),
                                  ('conversacional', 'Conversacional'),
                                  ('tecnico', 'Técnico'),
                                  ('narrativo', 'Narrativo')
                              ],
                              validators=[InputRequired(message='Por favor, selecione o estilo')])
    
    tone = SelectField('Tom',
                     choices=[
                         ('', 'Selecione o tom...'),
                         ('formal', 'Formal'),
                         ('informal', 'Informal'),
                         ('neutro', 'Neutro'),
                         ('persuasivo', 'Persuasivo'),
                         ('educativo', 'Educativo')
                     ],
                     validators=[InputRequired(message='Por favor, selecione o tom')])
    
    language_complexity = SelectField('Complexidade da Linguagem',
                                    choices=[
                                        ('', 'Selecione a complexidade...'),
                                        ('simples', 'Simples'),
                                        ('moderada', 'Moderada'),
                                        ('complexa', 'Complexa'),
                                        ('especializada', 'Especializada')
                                    ],
                                    validators=[InputRequired(message='Por favor, selecione a complexidade')])
    
    style_references = TextAreaField('Referências de Estilo',
                                   validators=[Optional(), Length(max=500)])

    # Step 5 fields
    estimated_length = SelectField('Tamanho Estimado',
                                 choices=[
                                     ('curto', 'Curto (500-1000 palavras)'),
                                     ('medio', 'Médio (1000-2500 palavras)'),
                                     ('longo', 'Longo (2500-5000 palavras)'),
                                     ('extenso', 'Extenso (5000+ palavras)')
                                 ],
                                 default='medio')
    
    output_format = SelectField('Formato de Saída',
                              choices=[
                                  ('markdown', 'Markdown'),
                                  ('html', 'HTML'),
                                  ('texto', 'Texto Simples'),
                                  ('docx', 'Word Document')
                              ],
                              default='markdown')
    
    special_requirements = TextAreaField('Requisitos Especiais',
                                       validators=[Optional(), Length(max=1000)])
    
    additional_notes = TextAreaField('Observações Adicionais',
                                   validators=[Optional(), Length(max=500)])
