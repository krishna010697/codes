clc
clear all
close all
img1 = imread('pepper.bmp');
img1=rgb2gray(img1);
img1=imresize(img1,[321 481]);
figure, imshow(img1), title('Original Image')
[m,n]=size(img1);
%number of ants
SearchAgents_no=25;
%number of thresholds for segmentation M=2,3,4,5
thresholds=2;
% Maximum number of iterations
Max_iteration=10;
ub=0;
lb=255;
%To find max and min value of pixel in image 
for i=1:m
    for j=1:n
        if(img1(i,j)>ub)
            ub=img1(i,j);
        end
    end
end
for i=1:m
    for j=1:n
        if(img1(i,j)<lb)
            lb=img1(i,j);
        end
    end
end
lb=double(lb);
ub=double(ub);
 t=cputime;
 % finding optimized threshold values for 5 iterations
 a=zeros(5,thresholds);
  for iter=1:5
      %call ALO function to find optimal threshold values(Best_pos)
      [~,Best_pos]=ALO(thresholds,SearchAgents_no,Max_iteration,lb,ub,img1);
      a(iter,:)=round(Best_pos);
      
  end
 %mean of 5 iterations    
      Best_pos=sort(round(sum(a)/5));
  display(['time elapsed: ', num2str(cputime-t)]);
   display(['Threshold values obtained by ALO is : ', num2str(Best_pos)]);
   
   %applying image segmentation for optimized thresholds
   value = [0 Best_pos(2:end) 255];
   Segmented_image= imquantize(img1, Best_pos, value);
   imshow(uint8(Segmented_image));
   
   display(['PSNR : ', num2str(psnr(img1,uint8(Segmented_image)))]);
   display(['SSIM : ', num2str(ssim(img1,uint8(Segmented_image)))]);
   display(['optimized fitness value : ', num2str(Get_Functions_details(Best_pos,img1))]);

