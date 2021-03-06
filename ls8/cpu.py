"""CPU functionality."""
import sys
class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.reg.append(0xf4)
        self.pc = 0
        self.FL = 0b00000000
        self.sp = 7
        self.instructions = {
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b10100000: self.ADD,
            0b10100001: self.SUB,
            # 0b10100011:self.DIV
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b00010001: self.RET,
            0b01010000: self.CALL,
            0b00000000: self.NOP,
            0b10100111: self.CMP,
            0b01010100: self.JMP,
            0b01010101: self.JEQ,
            0b01010110: self.JNE
        }

    def load(self):
        """Load a program into memory."""
        address = 0
        # For now, we've just hardcoded a program:
        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]
        program = []
        with open(sys.argv[1], 'r') as file:
            for line in file:
                get = line.find('#')
                if get >= 0:
                     line = line[:get]
                if len(line) > 1:
                    line = line.strip()
                    program.append(line)
        for instruction in program:
            self.ram[address] = int(instruction, 2)
            address += 1

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR]=MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            self.reg[reg_a] %= 0b100000000
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
            self.reg[reg_a] %= 0b100000000
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
            self.reg[reg_a] %= 0b100000000
        elif op =="CMP":
            if self.reg[reg_a]==self.reg[reg_b]:
                self.FL|=1
            else:
                self.FL&=0b11111110
      
        else:
            raise Exception("Unsupported ALU operation")

    # def trace(self):
    #     """
    #     Handy function to print out the CPU state. You might want to call this
    #     from run() if you need help debugging.
    #     """
    #     print(f"TRACE: %02X | %02X %02X %02X |" % (
    #         self.pc,
    #         self.FL,
    #         #self.ie,
    #         self.ram_read(self.pc),
    #         self.ram_read(self.pc + 1),
    #         self.ram_read(self.pc + 2)
    #     ), end='')
    #     for i in range(8):
    #         print(" %02X" % self.reg[i], end='')
    #     print()

    def LDI(self):
        self.pc+=1
        reg = self.ram_read(self.pc)
        self.pc+=1
        val = self.ram_read(self.pc)
        self.reg[reg] = val

    def PRN(self):
        self.pc+=1
        reg = self.ram[self.pc]
        print(self.reg[reg])

    def MUL(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.alu("MUL", op_a, op_b)
        self.pc += 2

    def ADD(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.alu("ADD", op_a, op_b)
        self.pc += 2

    def SUB(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.alu("SUB", op_a, op_b)
        self.pc += 2
    
    def PUSH(self):
        self.reg[self.sp] -= 1
        self.pc += 1
        reg = self.ram_read(self.pc)
        self.ram_write(self.reg[self.sp], self.reg[reg])
    
    def POP(self):
        self.pc += 1
        reg = self.ram_read(self.pc)
        data = self.ram_read(self.reg[self.sp])
        self.reg[reg] = data
        self.reg[self.sp] += 1
    
    def CALL(self):
        return_address = self.pc + 1 
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], return_address)
        reg_num = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg_num]
    
    def RET(self):
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
    
    def NOP(self):
        pass
    
    def CMP(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("CMP", reg_a, reg_b)
        self.pc += 2

    
    def JMP(self):
        # print('jmp')
        reg = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg]
        self.pc -= 1
    
    def JEQ(self):
        # print('jeq')
        reg = self.ram_read(self.pc + 1)
        if self.FL == 0b00000001:
            self.JMP()
        else:
            self.pc += 1
    
    def JNE(self):
        reg = self.ram_read(self.pc + 1)
        if self.FL != 0b00000001:
            self.JMP()
        else:
            self.pc += 1
       


    def run(self):
        """Run the CPU."""
        running = True
        while running:
            ir = self.ram[self.pc]
            if ir == 0b00000001:
                running = False
            else:
                # print('ir', ir)
                self.instructions[ir]()
                self.pc += 1 