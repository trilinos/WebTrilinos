// @HEADER
// ***********************************************************************
//
//               WebTrilinos: A Web Interface to Trilinos
//                 Copyright (2006) Sandia Corporation
//
// Under terms of Contract DE-AC04-94AL85000, there is a non-exclusive
// license for use of this work by or on behalf of the U.S. Government.
//
// This library is free software; you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation; either version 2.1 of the
// License, or (at your option) any later version.
//
// This library is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public
// License along with this library; if not, write to the Free Software
// Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301
// USA
// Questions? Contact Marzio Sala (marzio.sala _AT_ gmail.com)
//
// ***********************************************************************
// @HEADER

// This code should be run with at least two processes

#include "Epetra_ConfigDefs.h"
#ifdef HAVE_MPI
#include "mpi.h"
#include "Epetra_MpiComm.h"
#else
#include "Epetra_SerialComm.h"
#endif
#include "Epetra_Map.h"
#include "Epetra_Vector.h"
#include "Epetra_FECrsMatrix.h"

int main(int argc, char *argv[]) 
{
#ifdef HAVE_MPI
  MPI_Init(&argc, &argv);
  Epetra_MpiComm Comm(MPI_COMM_WORLD);
#else
  Epetra_SerialComm Comm;
#endif

  // Create a linear map of size 10 (could be any number > 1)
  int NumGlobalElements = 10;
  Epetra_Map Map(NumGlobalElements, 0, Comm);

  // create a diagonal FE crs matrix (one nonzero per row)
  Epetra_FECrsMatrix A(Copy,Map,1);
  
  // Next, set the matrix entries.
  //
  // Note 1: Matrix entries are only contributed from processor
  // 0, regardless of how many processors the program is running on.
  // Proc 0 fills the entire global matrix. Data that belongs in
  // matrix rows owned by procs 1 .. numprocs-1 gets sent to those
  // processors during the call to 'A.GlobalAssemble()' below.
  // 
  // Note 2: We fill the matrix using 'InsertGlobalValues'. An
  // alternative approach that would be more efficient for large
  // matrices in most cases would be to first create and fill a
  // graph (Epetra_FECrsGraph), then construct the matrix with the
  // graph (after calling graph.FillComplete) and fill the matrix
  // using the method 'SumIntoGlobalValues'.
   
  if (Comm.MyPID() == 0) 
  {
    for (int i = 0 ; i < NumGlobalElements ; ++i) 
    {
      double value = 1.0 * i;
      A.InsertGlobalValues(1, &i, 1, &i, &value);
    }
  }
  
  A.GlobalAssemble();

  cout << A;
  
#ifdef HAVE_MPI
  MPI_Finalize();
#endif

  return(EXIT_SUCCESS);
}
