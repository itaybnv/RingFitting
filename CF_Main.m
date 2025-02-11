% here the processing will be done, please set up the following parameters
% manually before running the code (cent_area, x0_image, y0_image, radmin, radmax, pixel_value_nm, pic_name)
app=[];
app.x0_image=66; %enter manually - initial guess for the x coordinate of the center in ImageJ [pixels]
app.y0_image=59; %enter manually - initial guess for the y coordinate of the center in ImageJ [pixels]
app.cent_area=5; %enter manually - distance around the initial guess at which the center will be searched.
app.radmin=8; %enter manually - minimal possible radius in [pixels]
app.radmax=12; %enter manually - maximal possible radius in [pixels]
app.pixel_value_nm=65; %enter manually - camera pixel size in [nanometers]
pic_name=sprintf('D:\\Anindita\\MatLab\\CircleFittingApp\\Example movies\\Time-Lapse-FtsZ.tif'); %enter manually - the full adreess of the movie



info=imfinfo(pic_name);
app.numFrames = numel(info); % Number of frames in the movie
for t=1:app.numFrames
    app.img_wBC(:,:,t) = imread(pic_name,t); %raw image
end

for t = 1:app.numFrames

    [R_main,C_main]=size(app.img_wBC(:,:,t)); %size of raw image
    BC_borders= [1,10,1,10];% The background is determined from a 10x10 area at the top left square of the image
    I_fluor_BC(:,:,t)=app.img_wBC(BC_borders(1):BC_borders(2),BC_borders(3):BC_borders(4),t); %Image of the background only
    mean_BC(t) = mean2(I_fluor_BC(:,:,t)); %mean background only
    stDev_BC(t)=std2(I_fluor_BC(:,:,t)); %standard deviation of background only
    mean_imageI_all(t) = mean2(app.img_wBC(:,:,t)); %mean intensity of the raw image
    img(:,:,t) = app.img_wBC(:,:,t)-mean_BC(t);  %image after background subtraction
    x0_matlab = app.x0_image+1; y0_matlab =app.y0_image+1; %imagej to matlab center coordinates
    Borders=[y0_matlab-15,y0_matlab + 15,x0_matlab - 15,x0_matlab + 15];
    Borders_mat(:,t) = Borders;% Borders - (y1,y2,x1,x2) - a rectangle that contains the ring
    I_fluor(:,:,t) = img(Borders(1):Borders(2),Borders(3):Borders(4),t);        %31x31 pixel image, with [x0_matlab,y0_matlab] (guess) as the center
    I_fluor(:,:,t) = double(I_fluor(:,:,t));

    if t==1
        fprintf('The value of radmin is: %g nm = %g pixel\n', app.radmin*app.pixel_value_nm,app.radmin);
        fprintf('The value of radmmax is: %g nm = %g pixel\n', app.radmax*app.pixel_value_nm,app.radmax);
    end
    % 1x - start with this
    a = CF_circle_contour_func(I_fluor(:,:,t),app.radmin,app.radmax,app.cent_area); %TBD - itegrate this function
    x0=a(1); y0=a(2); %the 1x center coordinates, in the 31x31 pixel image
    x0_mat(t) = x0; y0_mat(t) = y0;
    rad=a(3); % the 1x radius
    rad_mat(t) = rad;
    %fprintf('The value of 1x rad is: %g nm = %g pixel\n', rad*app.pixel_value_nm,rad);
    x0_1x_matlab = x0+Borders(3)-1; y0_1x_matlab = y0+Borders(1)-1; %the 1x center coordinates, in the [R_main x C_main] original uncropped image
    app.x0_image=x0_1x_matlab-1; app.y0_image=y0_1x_matlab-1; %matlab to imageJ center coordinates
    centers_1x =[x0_1x_matlab,y0_1x_matlab]; %1x centers_matlab
    x0_image_1x_mat(t)= app.x0_image; y0_image_1x_mat(t) = app.y0_image; %image 1x centers all frame
    [R,C]=size(I_fluor(:,:,t));
    %border adjustment to get centered image
    gap_x0 = abs(16-x0);
    gap_y0 = abs(16-y0);
    if (gap_x0>=gap_y0)
        gap= gap_x0+1;
    else
        gap=gap_y0+1;
    end
    gap_mat(t)= gap; %gap for all frames

    % 10x - If 1x work, move on to this
    %10x precision function
    b(:,:,t) = CF_circle_contour_func_X10(img(:,:,t),x0,y0,rad,gap,Borders,R,C); %TBD - integrate this function
    b2 = CF_circle_contour_func_X10_no_shift(img(:,:,t),x0,y0,rad,Borders,R,C); % best fit centers and radius
    x0_10x=b2(1);y0_10x=b2(2); %the 10x center coordinates, in the 31x31 pixel image
    r=b2(3); % the 10x radius
    fprintf('At frame %d The value of 10x r is: %g nm = %g pixel\n', t, r*app.pixel_value_nm,r);


    % Final centers and radius of the z-ring
    x02=b2(1); y02=b2(2); rad2=b2(3);
    centers =[x02,y02]; %unused
    x0_10x_matlab = x0_10x+Borders(3)-1; y0_10x_matlab = y0_10x+Borders(1)-1; %the 10x center coordinates, in the [R_main x C_main] original uncropped image
    x0_image_10x=x0_10x_matlab-1; y0_image_10x=y0_10x_matlab-1; %matlab to imageJ center coordinates

    centers_10x =[x0_10x_matlab,y0_10x_matlab]; %10x centers_matlab
    CentersArr_10x(t,1:2)=centers_10x;

    x0_image_10x_mat(t)= x0_image_10x; y0_image_10x_mat(t) = y0_image_10x; %image 10x centers all frame

    r_mat(t) = r; % best radii of all frame
    r_mean= mean(r_mat);
    r_std= std(r_mat);

    I_fluor3(:,:,t) = b(:,:,t); %final image% change to b1 when use cytoplasmic BC removal

    % % plotting
    
    % % Create an axes inside the figure
    % ax = axes(app.Figures10xRad(t)); % Create an axes handle in the new figure
    %
    % % Plot the image in the new axes
    % imagesc(ax, app.img_wBC(:, :, t)); % Use 'ax' as the target for imagesc
    % colormap(ax, gray);               % Set the colormap for the new axes
    %

     app.Figures10xRad(t)=figure;
     imagesc(app.img_wBC(:,:,t));colormap(gray);        
     hold on;
     px_circle=viscircles(centers_10x,r_mat(t),'EdgeColor','b'); % plot the circle bound area %10x precision
     plot(x0_10x_matlab, y0_10x_matlab,'.', 'color', 'red', 'markersize', 10); %plot the center %10x precision
     title(sprintf('Frame %g. Circle fit \n r=%g pixel = %g nm',t,round(r_mat(t),2), round(r_mat(t)*app.pixel_value_nm,2))) %*pixel_value_nm
     hold off;   
end
fprintf('Finished analyzing %d frames\n', app.numFrames);
app.AllR=r_mat;


%plot of Radius Vs. Frame
figure;
scatter(1:app.numFrames,app.AllR*app.pixel_value_nm,'MarkerFaceColor','k')
title('Radius Vs. Frame')
xlabel('Frame');ylabel('Radius(nm)');
ylim([min(app.AllR)*app.pixel_value_nm*0.9 max(app.AllR)*app.pixel_value_nm*1.1]);xlim([0 app.numFrames+1]);