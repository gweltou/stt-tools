
rm -rf training_data/train/*

cp -r sae/b* training_data/train/
cp -r dizale/* training_data/train/
cp -r rkb training_data/train/
cp -r various training_data/train/
cp -r common_voice/train/* training_data/train

rm -rf training_data/test/*

cp -r common_voice/test/* training_data/test
