#include <iostream>
#include <complex>

using namespace std;

main()
{
    complex<double> x(1.0e-10,0.0);
    complex<double> two(2.0,0.0);

    for(int i = 0; i < 10; ++i)
    {
	cout << x << "\n"; 
	x = pow(x,two);
    }
}
