import numpy as np

from ...utils.collections import dotdict


def loadDefaultParams(Cmat=None, Dmat=None, seed=None):
    """Load default parameters for the Wilson-Cowan model

    :param Cmat: Structural connectivity matrix (adjacency matrix) of coupling strengths, will be normalized to 1. If not given, then a single node simulation will be assumed, defaults to None
    :type Cmat: numpy.ndarray, optional
    :param Dmat: Fiber length matrix, will be used for computing the delay matrix together with the signal transmission speed parameter `signalV`, defaults to None
    :type Dmat: numpy.ndarray, optional
    :param seed: Seed for the random number generator, defaults to None
    :type seed: int, optional

    :return: A dictionary with the default parameters of the model
    :rtype: dict
    """

    params = dotdict({})

    ### runtime parameters
    params.dt = 0.1  # ms 0.1ms is reasonable
    params.duration = 2000  # Simulation duration (ms)
    np.random.seed(seed)  # seed for RNG of noise and ICs
    params.seed = seed

    # ------------------------------------------------------------------------
    # global whole-brain network parameters
    # ------------------------------------------------------------------------

    # signal transmission speed between areas
    params.signalV = 20.0
    params.K_gl = 0.6  # global coupling strength

    if Cmat is None:
        params.N = 1
        params.Cmat = np.zeros((1, 1))
        params.lengthMat = np.zeros((1, 1))

    else:
        params.Cmat = Cmat.copy()  # coupling matrix
        np.fill_diagonal(params.Cmat, 0)  # no self connections
        params.N = len(params.Cmat)  # number of nodes
        params.lengthMat = Dmat

    # ------------------------------------------------------------------------
    # local node parameters
    # ------------------------------------------------------------------------

    # external input parameters:
    params.tau_ou = 5.0  # ms Timescale of the Ornstein-Uhlenbeck noise process
    params.sigma_ou = 0.0  # noise intensity
    params.exc_ou_mean = 0.0  # OU process mean
    params.inh_ou_mean = 0.0  # OU process mean

    # neural mass model parameters
    params.tau_exc = 2.5  # excitatory time constant
    params.tau_inh = 3.75  # inhibitory time constant
    params.c_excexc = 16  # local E-E coupling
    params.c_excinh = 15  # local E-I coupling
    params.c_inhexc = 12  # local I-E coupling
    params.c_inhinh = 3  # local I-I coupling
    params.a_exc = 1.5  # excitatory gain
    params.a_inh = 1.5  # inhibitory gain
    params.mu_exc = 3.0  # excitatory firing threshold
    params.mu_inh = 3.0  # inhibitory firing threshold
    
    # adaptation parameters 
    params.tau_adap = 100.0 # adaptation time constant
    params.a_adap = 0.5 # adaptation gain
    params.a_a = 3.0 # adaptation gain
    params.mu_a = 2.0 # adaptation threshold


    # values of the external inputs
    params.exc_ext = 0.0  # baseline external input to E
    params.inh_ext = 0.0  # baseline external input to I
    

    # ------------------------------------------------------------------------

    params.exc_init = 0.05 * np.random.uniform(0, 1, (params.N, 1))
    params.inh_init = 0.05 * np.random.uniform(0, 1, (params.N, 1))
    
    # initial condition adaptation
    params.adap_init = 0.05 * np.random.uniform(0, 1, (params.N, 1))

    # Ornstein-Uhlenbeck noise state variables
    params.exc_ou = np.zeros((params.N,))
    params.inh_ou = np.zeros((params.N,))
    
    # turn True, If you want to add a step current for one second, two seconds before end
    params.step_current = False
    params.from_second = 2
    params.to_second = 1
    params.ext_val = 1.0
    
    # turn True, If you want to add a negative step current from second to second before end to push it into down
    params.neg_from_second = 5
    params.neg_to_second = 4
    params.neg_ext_val = -1.0

    return params


def computeDelayMatrix(lengthMat, signalV, segmentLength=1):
    """Compute the delay matrix from the fiber length matrix and the signal velocity

    :param lengthMat:       A matrix containing the connection length in segment
    :param signalV:         Signal velocity in m/s
    :param segmentLength:   Length of a single segment in mm

    :returns:    A matrix of connexion delay in ms
    """

    normalizedLenMat = lengthMat * segmentLength
    # Interareal connection delays, Dmat(i,j) in ms
    if signalV > 0:
        Dmat = normalizedLenMat / signalV
    else:
        Dmat = lengthMat * 0.0
    return Dmat
