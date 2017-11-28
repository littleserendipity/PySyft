import zmq

class FloatTensor():
    
    def __init__(self, controller, data, data_is_pointer = False, verbose=False):
        self.verbose = verbose
        self.controller = controller
        if(data is not None and not data_is_pointer):
            data = data.astype('float')
            controller.socket.send_json({"objectType"   :"tensor",
                                         "functionCall" :"create",
                                         "data"         : list(data.flatten()),
                                         "shape"        : data.shape})
            self.id = int(controller.socket.recv_string())
            print("FloatTensor.__init__: " +  str(self.id))

        elif(data_is_pointer):
            self.id = int(data)

    # TODO: this fails with x = x + x if x is a FloatTensor
    # def __del__(self):
        # self.delete_tensor()

    def __add__(self,x):

        if(type(x) == FloatTensor):
            self.controller.socket.send_json(self.cmd("add_elem",[x.id])) # sends the command
        else:   
            self.controller.socket.send_json(self.cmd("add_scalar",[str(x)])) # sends the command
        return FloatTensor(self.controller,int(self.controller.socket.recv_string()),True)

    def __iadd__(self,x):
        if(type(x) == FloatTensor):
            self.controller.socket.send_json(self.cmd("add_elem_",[x.id])) # sends the command
        else:   
            self.controller.socket.send_json(self.cmd("add_scalar_",[str(x)])) # sends the command
        return FloatTensor(self.controller,int(self.controller.socket.recv_string()),True)



    def delete_tensor(self):
        
        self.controller.socket.send_json({"functionCall":"deleteTensor", "objectIndex": self.id})
        self.verbose = None
        self.controller = None
        self.id = None

    def __mul__(self,x):
        return self.params_func("mul",[x.id],return_response=True)

    def __repr__(self):
        return self.no_params_func("print",True,False)

    def __str__(self):
        return self.no_params_func("print",True,False)

    def __sub__(self,x):
        return self.params_func("sub",[x.id],return_response=True)
    
    def abs(self):
        return self.no_params_func("abs",return_response=True)
      
    def abs_(self):
        return self.no_params_func("abs_")

    def neg(self):
        return self.no_params_func("neg")

    def addmm_(self, x,y):
        return self.params_func("addmm_",[x.id,y.id])

    def addmm(self, x,y):
        copy = self.copy()
        copy.params_func("addmm_",[x.id,y.id])
        return copy

    def cmd(self,functionCall,tensorIndexParams=[]):
        cmd = {
            'functionCall'      :functionCall,
            'objectType'        :'tensor',
            'objectIndex'       :self.id,
            'tensorIndexParams' :tensorIndexParams}
        return cmd

    def copy(self):
        return self.no_params_func("copy", return_response=True)

    def cpu(self):
        return self.no_params_func("cpu")

    def delete_tensor(self):
        if(self.id is not None):
            self.no_params_func("delete")
        self.verbose = None
        self.controller = None
        self.id = None

    def floor_(self):
    	return self.no_params_func("floor_")

    # Fills this tensor with zeros.
    def zero_(self):
        return self.no_params_func("zero_")

    def gpu(self):
        return self.no_params_func("gpu")

    def neg(self):
        return self.no_params_func("neg",return_response=True)
    
    def params_func(self, name, params, return_response=False,return_as_tensor=True):        
        # send the command
        self.controller.socket.send_json(self.cmd(name,tensorIndexParams=params))
        # receive output from command
        res = self.controller.socket.recv_string()

        if(self.verbose):
            print(res)

        if(return_response):
            if(return_as_tensor):
                print("FloatTensor.__init__: " +  res)
                return FloatTensor(self.controller,int(res),True)
            else:
                return res
        return self

    def no_params_func(self, name, return_response=False,return_as_tensor=True):
        return( self.params_func(name,[],return_response,return_as_tensor) )

    def scalar_multiply(self, scalar):
        return self.params_func("scalar_multiply",[scalar],return_response=True)
    
    def sigmoid_(self):
        return self.no_params_func("sigmoid_")

class SyftController():

    def __init__(self, identity):

        self.identity = identity

        context = zmq.Context()
        self.socket = context.socket(zmq.DEALER)
        self.socket.setsockopt_string(zmq.IDENTITY, identity)
        self.socket.connect("tcp://localhost:5555")

    def FloatTensor(self,data):
        return FloatTensor(self,data)
