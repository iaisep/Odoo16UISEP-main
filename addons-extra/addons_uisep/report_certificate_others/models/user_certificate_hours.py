from odoo import models, fields, api,_
import logging
_logger = logging.getLogger(__name__)
class CustomSurveySurvey(models.Model):

    _inherit = 'survey.survey'
  

    backgroundimage=fields.Binary(string="Imagen de fondo")

    firm_response=fields.Binary(string="Firma de responsable")

    body_certification=fields.Html(string="Cuerpo de certificado", translate=True)

    title_certification=fields.Char(string="Titulo de certificado", translate=True)

    ref_certification=fields.Char(string="Referencia de certificado", translate=True)

    studen_school=fields.Char(string="Escuela", translate=True)

    motivational=fields.Char(string="Motivacional", translate=True)

    firm_direction=fields.Char(string="Text General", translate=True)

    firm_firm=fields.Char(string="Text Académico", translate=True)

    

   
    # ------------------------------------------------------------
    # ANSWER MANAGEMENT
    # ------------------------------------------------------------

    def _create_answer(self, user=False, partner=False, email=False, test_entry=False, check_attempts=True, **additional_vals):
        """ Main entry point to get a token back or create a new one. This method
        does check for current user access in order to explicitely validate
        security.

          :param user: target user asking for a token; it might be void or a
                       public user in which case an email is welcomed;
          :param email: email of the person asking the token is no user exists;
        """
        self.check_access_rights('read')
        self.check_access_rule('read')

        user_inputs = self.env['survey.user_input']
        for survey in self:
            if partner and not user and partner.user_ids:
                user = partner.user_ids[0]

            invite_token = additional_vals.pop('invite_token', False)
            survey._check_answer_creation(user, partner, email, test_entry=test_entry, check_attempts=check_attempts, invite_token=invite_token)
            data_survey=self.env['survey.survey'].search([('id','=',survey.id)])
            answer_vals = {
                'survey_id': survey.id,
                'test_entry': test_entry,
                'is_session_answer': survey.session_state in ['ready', 'in_progress'],               
                'backgroundimage':data_survey.backgroundimage, 
                'certification':data_survey.certification, 
                'firm_response':data_survey.firm_response, 
                'response':data_survey.user_id.name,
                'body_certification':data_survey.body_certification,
                'title_certification':data_survey.title_certification,
                'ref_certification':data_survey.ref_certification,
                'studen_school':data_survey.studen_school,
                'motivational':data_survey.motivational,
                'firm_direction':data_survey.firm_direction,
                'firm_firm':data_survey.firm_firm,
            }
            if survey.session_state == 'in_progress':
                # if the session is already in progress, the answer skips the 'new' state
                answer_vals.update({
                    'state': 'in_progress',
                    'start_datetime': fields.Datetime.now(),
                })
            if user and not user._is_public():
                answer_vals['partner_id'] = user.partner_id.id
                answer_vals['email'] = user.email
                answer_vals['nickname'] = user.name
            elif partner:
                answer_vals['partner_id'] = partner.id
                answer_vals['email'] = partner.email
                answer_vals['nickname'] = partner.name
            else:
                answer_vals['email'] = email
                answer_vals['nickname'] = email

            if invite_token:
                answer_vals['invite_token'] = invite_token
            elif survey.is_attempts_limited and survey.access_mode != 'public':
                # attempts limited: create a new invite_token
                # exception made for 'public' access_mode since the attempts pool is global because answers are
                # created every time the user lands on '/start'
                answer_vals['invite_token'] = self.env['survey.user_input']._generate_invite_token()

            answer_vals.update(additional_vals)
            user_inputs += user_inputs.create(answer_vals)

        for question in self.mapped('question_ids').filtered(
                lambda q: q.question_type == 'char_box' and (q.save_as_email or q.save_as_nickname)):
            for user_input in user_inputs:
                if question.save_as_email and user_input.email:
                    user_input.save_lines(question, user_input.email)
                if question.save_as_nickname and user_input.nickname:
                    user_input.save_lines(question, user_input.nickname)

        return user_inputs

   
class CustomSurveyUser_input(models.Model):

    _inherit = 'survey.user_input'

    backgroundimage=fields.Binary(string="Imagen de fondo")  

    certification=fields.Boolean(string="Certificado")   

    firm_response=fields.Binary(string="Firma de responsable")  

    response=fields.Char(string="responsable")  

    body_certification=fields.Html(string="Cuerpo de certificado", translate=True)

    title_certification=fields.Char(string="Titulo de certificado", translate=True)

    ref_certification=fields.Char(string="Referencia de certificado", translate=True)

    studen_school=fields.Char(string="Escuela", translate=True)

    motivational=fields.Char(string="Motivacional", translate=True)

    firm_direction=fields.Char(string="Text General", translate=True)

    firm_firm=fields.Char(string="Text Académico", translate=True)

