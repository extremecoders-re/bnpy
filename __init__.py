from binaryninja import *

import dis
import struct


class Python(Architecture):
    name = 'Python'
    max_instr_length = 3
    
    # SP register is required, even if we are not going to use it
    regs = {'sp': RegisterInfo('sp', 2)}
    stack_pointer = 'sp'

    
    def perform_get_instruction_info(self, data, addr):
        opkode = struct.unpack('<B', data[0])[0]
        i_info = InstructionInfo()        
        
        
        # Invalid instruction
        if opkode not in dis.opmap.values():
            i_info = None
            #i_info.length = 1
            #i_info.add_branch(BranchType.UnresolvedBranch)
            
        elif opkode < dis.HAVE_ARGUMENT:
            mnemonic = dis.opname[opkode]
            i_info.length = 1
            if mnemonic == 'RETURN_VALUE':
                i_info.add_branch(BranchType.FunctionReturn)
                
        else:
            mnemonic = dis.opname[opkode]
            arg = struct.unpack('<h', data[1:3])[0]
            i_info.length = 3
            
            if mnemonic in ('JUMP_IF_FALSE_OR_POP', 'POP_JUMP_IF_FALSE'):
                i_info.add_branch(BranchType.TrueBranch, addr + 3)
                i_info.add_branch(BranchType.FalseBranch, arg)
                
            elif mnemonic in ('JUMP_IF_TRUE_OR_POP', 'POP_JUMP_IF_TRUE'):
                i_info.add_branch(BranchType.TrueBranch, arg)
                i_info.add_branch(BranchType.FalseBranch, arg + 3)
                
            elif mnemonic in ('JUMP_ABSOLUTE', 'CONTINUE_LOOP'):
                i_info.add_branch(BranchType.UnconditionalBranch, arg)
                
            elif mnemonic in ('FOR_ITER', 'JUMP_FORWARD'):
                i_info.add_branch(BranchType.UnconditionalBranch, addr + arg + 3)
                    
        return i_info    
        

    def perform_get_instruction_text(self, data, addr):        
        opkode = struct.unpack('<B', data[0])[0]
        
        # Invalid instruction
        if opkode not in dis.opmap.values():
            return None
        
        tokens = []
        mnemonic = dis.opname[opkode]
        insn_length = 1

        tokens.append(InstructionTextToken(InstructionTextTokenType.InstructionToken, mnemonic))
        
        if opkode >= dis.HAVE_ARGUMENT:
            arg = struct.unpack('<h', data[1:3])[0]
            tokens.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ''.rjust(22 - len(mnemonic))))

            if opkode in dis.hasjabs:
                tokens.append(InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, format(arg, 'x')))    

            elif opkode in dis.hasjrel:
                tokens.append(InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, format(addr + arg + 3, 'x')))    
            else:
                tokens.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, str(arg)))
            insn_length = 3
            
        return tokens, insn_length


    def perform_get_instruction_low_level_il(self, data, addr, il):
        #Not implemented
        return None


Python.register()