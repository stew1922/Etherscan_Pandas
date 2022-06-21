import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='etherscan-analytics',  
     version='0.1',
     scripts=['etherscan.etherscan'] ,
     author="Travis Stewart",
     author_email="stew1922@gmail.com",
     description="An analytics tool for the Ethereum blockchain utilizing Etherscan API",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/stew1922/Etherscan_Analytics",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )