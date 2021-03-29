import os
import random

import numpy as np
import pandas as pd
from twitchio.ext import commands


CSV_PATH = (
    r'C:\Users\gusb\Python\doodleprompt\what-to-draw-2021_03_24-1429.csv'
)

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            irc_token=os.environ['TMI_TOKEN'],
            client_id=os.environ['CLIENT_ID'],
            nick=os.environ['BOT_NICK'],
            prefix='!',
            initial_channels=[os.environ['CHANNEL']]
        )
        # Check that CSV_PATH exists
        if os.path.exists(CSV_PATH):
            self.df = pd.read_csv(CSV_PATH)
        else:
            raise ValueError('CSV not found')
        self.last_arg_tuple = None

    # Events don't need decorators when subclassed
    async def event_ready(self):
        print(f"{os.environ['BOT_NICK']} is online!")
        ws = bot._ws  # this is only needed to send messages within event_ready
        await ws.send_privmsg(os.environ['CHANNEL'], f"/me has landed!")

    # Look through messages for commands
    async def event_message(self, message):
        await self.handle_commands(message)

    # Ignore commands that aren't defined in this file
    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            return

    # async def event_message(self, message):
    #     try:
    #         await self.handle_commands(message)
    #     except commands.errors.CommandNotFound:
    #         return

    # Commands use a decorator...
    @commands.command(name='test')
    async def test_command(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')

    @commands.command(name='prompt')
    async def prompt_command(self, ctx, *args):
        # If no arguments are passed after the command
        if len(args) == 0:
            prompt_no_args_message = (
                f'Try making a sentence with some of these keywords: '
                f"{', '.join(self.df.columns)}"
                )
            await ctx.send(prompt_no_args_message)
        else:
            self.last_arg_tuple = args
            prompt = self.get_prompt(args)
            await ctx.send(prompt)

    @commands.command(name='reroll')
    async def reroll_command(self, ctx):
        if self.last_arg_tuple is None:
            await ctx.send('Try calling !prompt first!')
        else:
            prompt = self.get_prompt(self.last_arg_tuple)
            await ctx.send(prompt)

    def get_prompt(self, arg_tuple):
        prompt_list = [
            self.get_random_entry(arg) if arg in self.df.columns.values 
            else arg for arg in arg_tuple
        ]
        prompt_list = self.check_grammar(prompt_list)
        prompt = ' '.join(prompt_list)
        print(prompt)
        return prompt

    def get_random_entry(self, col):
        rand_entry = random.choice(self.df[col])
        if pd.isnull(rand_entry):
            rand_entry = self.get_random_entry(col)
        elif rand_entry in self.df.columns.values:
            rand_entry = self.get_random_entry(rand_entry)

        return rand_entry

    def check_grammar(self, prompt_list):
        for i, word in enumerate(prompt_list):
            if word == 'a':
                # If the next word in prompt_list starts with a vowel:
                if prompt_list[i + 1][0] in 'aeiou':
                    # Replace the item at this position in prompt_list (word)
                    # with 'an' instead of 'a'
                    prompt_list[i] = 'an'
            elif word == 'an':
                # If the next word in prompt_list does not start with a vowel:
                if prompt_list[i + 1][0] not in 'aeiou':
                    # Replace the item at this position in prompt_list (word)
                    # with 'a' instead of 'an'
                    prompt_list[i] = 'a'

        return prompt_list
                
                
if __name__ == "__main__":
    # from dotenv import load_dotenv
    # load_dotenv()
    bot = Bot()
    bot.run()

