run("Stack Splitter", "number=2");
waitForUser("Click OK to continue");

// channel 1
resetMinAndMax();
setMinAndMax(0, 60000);
run("8-bit");
run("Subtract Background...", "rolling=50 stack");
slicenumber = nSlices/2;
run("Z Project...", "start=1 stop=slicenumber projection=[Max Intensity]");
run("Copy to System");
close();
waitForUser("Click OK to continue");

//second part
slicenumber = nSlices/2;
run("Z Project...", "start=slicenumber projection=[Max Intensity]");
run("Copy to System");
close();
close();
waitForUser("Click OK to continue");

// channel 2
resetMinAndMax();
// For mz
//setMinAndMax(0, 40000);
//for pachynema
setMinAndMax(0, 70000);
//setMinAndMax(0, 150000);
run("8-bit");
run("Subtract Background...", "rolling=50 stack");
slicenumber = nSlices/2+1;
run("Z Project...", "start=1 stop=slicenumber projection=[Max Intensity]");
run("Copy to System");
close();
waitForUser("Click OK to continue");

//second part
slicenumber = nSlices/2+1;
run("Z Project...", "start=slicenumber projection=[Max Intensity]");
run("Copy to System");
close();
close();
waitForUser("Click OK to continue");

// channel 3
resetMinAndMax();
setMinAndMax(0, 110000);
//setMinAndMax(0, 100000);
//setMinAndMax(0, 500000);
run("8-bit");
run("Subtract Background...", "rolling=50 stack");
slicenumber = nSlices/2+2;
run("Z Project...", "start=1 stop=slicenumber projection=[Max Intensity]");
run("Copy to System");
close();
waitForUser("Click OK to continue");

//second part
slicenumber = nSlices/2+2;
run("Z Project...", "start=slicenumber projection=[Max Intensity]");
run("Copy to System");
close();
close();
waitForUser("Click OK to continue");

// channel 4
resetMinAndMax();
setMinAndMax(0, 170000);
run("8-bit");
run("Subtract Background...", "rolling=50 stack");
slicenumber = nSlices/2+3;
run("Z Project...", "start=1 stop=slicenumber projection=[Max Intensity]");
run("Copy to System");
//second part
slicenumber = nSlices/2+3;
run("Z Project...", "start=slicenumber projection=[Max Intensity]");
run("Copy to System");
















//Diakinesis
run("Stack Splitter", "number=3");
//DAPI
resetMinAndMax();
setMinAndMax(0, 40000);
run("8-bit");
run("Subtract Background...", "rolling=50 stack");
run("Z Project...", "projection=[Max Intensity]");
run("Copy to System");
close();
close();

//second
resetMinAndMax();
setMinAndMax(20, 110000);
run("8-bit");
run("Subtract Background...", "rolling=50 stack");
run("Z Project...", "projection=[Max Intensity]");
run("Copy to System");
close();
close();

//third
resetMinAndMax();
setMinAndMax(150, 80000);
run("8-bit");
run("Subtract Background...", "rolling=50 stack");
run("Z Project...", "projection=[Max Intensity]");
run("Copy to System");
close();
close();
