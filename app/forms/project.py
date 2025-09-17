from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileField, FileAllowed, FileRequired

class ProjectForm(FlaskForm):
    """Formulário para criar/editar um projeto"""
    title = StringField('Título', validators=[
        DataRequired(message='O título é obrigatório'),
        Length(max=200, message='O título não pode ter mais de 200 caracteres')
    ])
    
    description = TextAreaField('Descrição', validators=[
        Optional(),
        Length(max=1000, message='A descrição não pode ter mais de 1000 caracteres')
    ])
    
    status = SelectField('Status', choices=[
        ('draft', 'Rascunho'),
        ('active', 'Ativo'),
        ('paused', 'Pausado'),
        ('archived', 'Arquivado')
    ], validators=[DataRequired()])
    
    language = SelectField('Idioma', choices=[
        ('pt-BR', 'Português (Brasil)'),
        ('en-US', 'English (US)'),
        ('es-ES', 'Español')
    ], default='pt-BR')
    
    visibility = SelectField('Visibilidade', choices=[
        ('private', 'Privado (apenas você)'),
        ('team', 'Time (membros da equipe)'),
        ('public', 'Público (qualquer pessoa com o link)')
    ], default='private')
    
    submit = SubmitField('Salvar e Iniciar')

class ProjectSettingsForm(FlaskForm):
    """Formulário para configurações avançadas do projeto"""
    auto_save = BooleanField('Salvamento automático', 
                           default=True,
                           description='Salvar automaticamente as alterações')
    
    notifications = BooleanField('Notificações por e-mail', 
                               default=True,
                               description='Receber notificações sobre este projeto')
    
    export_format = SelectField('Formato de exportação padrão',
                              choices=[
                                  ('markdown', 'Markdown (.md)'),
                                  ('html', 'HTML (.html)'),
                                  ('pdf', 'PDF (.pdf)'),
                                  ('docx', 'Word (.docx)')
                              ],
                              default='markdown')
    
    api_access = BooleanField('Acesso via API',
                            default=False,
                            description='Permitir acesso a este projeto via API')
    
    submit = SubmitField('Salvar configurações')

class ImportProjectForm(FlaskForm):
    """Formulário para importar um projeto"""
    project_file = FileField('Arquivo do projeto', validators=[
        FileRequired(),
        FileAllowed(['zip'], 'Apenas arquivos ZIP são permitidos')
    ])
    
    import_executions = BooleanField('Importar histórico de execuções',
                                   default=True,
                                   description='Incluir o histórico de execuções na importação')
    
    submit = SubmitField('Importar Projeto')

class ExportProjectForm(FlaskForm):
    """Formulário para exportar um projeto"""
    include_executions = BooleanField('Incluir histórico de execuções',
                                    default=True,
                                    description='Incluir todo o histórico de execuções')
    
    format = SelectField('Formato de exportação',
                        choices=[
                            ('zip', 'ZIP (completo)'),
                            ('json', 'JSON (apenas dados)'),
                            ('markdown', 'Markdown (apenas conteúdo)')
                        ],
                        default='zip')
    
    submit = SubmitField('Exportar Projeto')
